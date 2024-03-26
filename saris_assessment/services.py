
import sys
import io
from abc import ABC, abstractmethod
from typing import List
from tablib import Dataset
from django_renderpdf import helpers
from django.core.files import File
from django.db.models import F, Sum, Max
from saris.utils import get_template_name
from account.models import Staff
from account.services import Signatory
from saris_admission.models import Enrollment, EnrollmentStatus, WithdrawalType
from saris_admission.services import StudentWithdrawal
from saris_assessment.models import SemesterResult
from saris_assessment.apps import SarisAssessmentConfig
from saris_calendar.models import AcademicSemester
from saris_curriculum.models import ConfiguredCourse, CourseType, MasterCurriculum, Program
from saris_curriculum.services import CurriculumManager
from saris_institution.models import Department, Campus, Faculty
from saris_registration.models import Registration, RegistrationType
from saris_students.models import Student
from .exceptions import (
    AssessmentRuleNotFoundException,
    CASBenchMarkError,
    CourseAppealsNotFoundException, 
    EOSBenchMarkError,
    SupplementaryNotFoundException
)
from .models import (
    AppealStatus,
    AssessmentVersion,
    AwardScheme,
    CompensationRule,
    CourseAppeal,
    GradeBook,
    GradeSchemeVersion,
    PassMark,
    PublishedGrade,
    PublishedResult,
    SUPStatus,
    SemesterResult, 
    AssessmentRule,
    GradeBenchMark, 
    CourseAttempt, 
    GradeScheme, 
    ResultDescription, 
    ResultType, 
    StudentCourse,
    LecturerCourse,
    Supplementary
)


class Settings(object):
    FIRST_YEAR_SEMESTERS = 2
    SEMESTER_INCREMENT = 1


#### COURSE ALLOCATION ####
class CourseAllocation(ABC):

    def __init__(self, lecturer, campus=None, academic_semester=None):

        if isinstance(lecturer, Staff):
            self.lecturer = lecturer
        else:
            self.lecturer = Staff.objects.get(pk=lecturer)

        if not campus:
            self.campus = lecturer.campus
        else:
            self.campus = campus

        if not academic_semester:
            self.academic_semester = self._get_academic_semester()
        elif isinstance(academic_semester, AcademicSemester):
            self.academic_semester = academic_semester
        else:
            self.academic_semester = AcademicSemester.get_by_id(academic_semester)  

    def _get_academic_semester(self):
        if not self.campus:
            return None
        elif AcademicSemester.has_active(self.campus):
            return AcademicSemester.get_active(self.campus)
        else:
            return None


class SingleClass(CourseAllocation):

    def __init__(self, lecturer_course: LecturerCourse, campus=None, academic_semester=None):
        self.pk = lecturer_course.pk
        self.course = lecturer_course.course
        self.grade_bench_mark = GradeBenchMark.get_active()
        super().__init__(lecturer=lecturer_course.lecturer,campus=campus, academic_semester=academic_semester)

    def get_class(self):
        return StudentCourse.objects.filter(
            course=self.course,
            academic_semester=self.academic_semester,
            enrollment__campus=self.campus
        ).exclude(
            enrollment__status=EnrollmentStatus.WITHDRAWAL
        )

    def get_grades(self):
        return StudentCourse.objects.filter(
            course=self.course,
            academic_semester=self.academic_semester,
            enrollment__campus=self.campus
        ).exclude(
            continous_grade=None,
            endsemester_grade=None,
            final_grade=None
        )

    def get_missing(self):
        return StudentCourse.objects.filter(
            course=self.course,
            academic_semester=self.academic_semester,
            enrollment__campus=self.campus,
            continous_grade=None,
            endsemester_grade=None,
            final_grade=None
        )

    def has_student(self, student_number) -> bool:
        return StudentCourse.objects.filter(
            course=self.course,
            academic_semester=self.academic_semester,
            enrollment__campus=self.campus,
            enrollment__student__student_number=student_number
        ).exists()

    def get_registration(self, student_number):
        return StudentCourse.objects.filter(
            course=self.course,
            academic_semester=self.academic_semester,
            enrollment__campus=self.campus,
            enrollment__student__student_number=student_number
        ).first()

    @property
    def class_size(self) -> int:
        return StudentCourse.objects.filter(
            course=self.course,
            academic_semester=self.academic_semester,
            enrollment__campus=self.campus
        ).count()

    @property
    def total_male(self) -> int:
        return StudentCourse.objects.filter(
            course=self.course,
            academic_semester=self.academic_semester,
            enrollment__campus=self.campus,
            enrollment__student__gender='Male'
        ).count()

    @property
    def total_female(self) -> int:
        return StudentCourse.objects.filter(
            course=self.course,
            academic_semester=self.academic_semester,
            enrollment__campus=self.campus,
            enrollment__student__gender='Female'
        ).count()

    @property
    def total_grades(self) -> int:
        return self.get_grades().count()

    @property
    def total_missing(self) -> int:
        return self.get_missing().count()

    @property
    def grade_submission(self) -> int:
        total_students = self.class_size()
        total_grades = self.total_grades()
        return int((total_grades/total_students) * 100)


class MultipleClass(CourseAllocation):

    def __init__(self, lecturer, campus=None, academic_semester=None):
        super().__init__(lecturer, campus, academic_semester)

    def _get_course_list(self):
        return StudentCourse.objects.filter(
            academic_semester=self.academic_semester,
            enrollment__campus=self.campus,
        ).exclude(
            enrollment__status=EnrollmentStatus.WITHDRAWAL
        ).values_list('course_id', flat=True).distinct()

    def _get_single_class(self, lecturer_course):
        single_class = SingleClass(
            lecturer_course=lecturer_course,
            campus=self.campus, 
            academic_semester=self.academic_semester
        )
        return single_class

    def _get_multi_class(self, lecturer_courses):
        multi_class = []
        for lecturer_course in lecturer_courses:
            single_class = self._get_single_class(lecturer_course)
            multi_class.append(single_class)
        return multi_class

    def get_courses(self):
        registered_list = self._get_course_list()
        lecturer_courses = LecturerCourse.objects.filter(lecturer=self.lecturer).filter(
            course_id__in=registered_list
        )
        return self._get_multi_class(lecturer_courses)

    def has_courses(self):
        registered_list = self._get_course_list()
        return LecturerCourse.objects.filter(lecturer=self.lecturer).filter(
            course_id__in=registered_list
        ).exists()


class CourseRegistration(CourseAllocation):

    def __init__(self, lecturer, campus=None, academic_semester=None):
        super().__init__(lecturer, campus, academic_semester)

    def get_campus_list(self):
        campuses = Campus.objects.all()
        return campuses

    def get_registration(self):
        registration = MultipleClass(
            lecturer=self.lecturer, 
            academic_semester=self.academic_semester, 
            campus=self.campus
        )
        if registration.has_courses():
            return registration

    def get_registrations(self):
        campuses = self.get_campus_list()
        registrations = []
        for campus in campuses:
            registration = MultipleClass(
                lecturer=self.lecturer, 
                academic_semester=self.academic_semester, 
                campus=campus
            )
            if registration.has_courses():
                registrations.append(registration)
        return registrations

    def has_registration(self):
        registrations = self.get_registrations()
        if len(registrations) > 0:
            return True
        else:
            return False


class CourseAllocationManager(object):

    def __init__(self, lecturer, courses: list) -> None:
        self.lecturer = lecturer
        self.courses = courses

    def process(self):
        for course in self.courses:
            LecturerCourse.objects.create(
                course_id=course,
                lecturer_id=self.lecturer
            )

#### END COURSE ALLOCATION ####


#### GRADE ENTRY #####
class GradeImport(SingleClass):

    def __init__(self, lecturer_course, campus=None, academic_semester=None):
        super().__init__(lecturer_course, campus, academic_semester)

    def _check_headers(self, dataset: Dataset):
        headers = dataset.headers

        if "STUDENT_NUMBER" not in headers:
            raise Exception("STUDENT_NUMBER Not Found")

        if "CAS_GRADE" not in headers:
            raise Exception("CAS_GRADE Not Found")

        if "EOS_GRADE" not in headers:
            raise Exception("EOS_GRADE Not Found")

    def import_data(self, dataset: Dataset):

        self._check_headers(dataset)

        for row in dataset.dict:
            student_number = row["STUDENT_NUMBER"]
            continous_grade = row["CAS_GRADE"]
            endsemester_grade = row["EOS_GRADE"]

            if self.has_student(student_number):
                student_course = self.get_registration(student_number)
                manager = GradeEntry(student_course, continous_grade, endsemester_grade)
                manager.process()


class GradeEntry(object):
    
    def __init__(self, student_course, continous_grade, endsemester_grade):
        if isinstance(student_course, StudentCourse):
            self.student_course = student_course
        else:
            self.student_course = StudentCourse.get_by_id(student_course)

        self.continous_grade = continous_grade
        self.endsemester_grade = endsemester_grade
        self.grade_bench_mark = GradeBenchMark.get_active()
        self.grade_scheme_version = GradeSchemeVersion.get_active()
    
    def _get_grade_scheme(self, final_grade):
        grade_scheme = GradeScheme.objects.filter(
            grade_scheme_version=self.grade_scheme_version,
            min_grade__lte=final_grade, 
            max_grade__gte=final_grade
        ).first()
        return grade_scheme

    def _save_continuous_grade(self):
        student = self.student_course.enrollment.student_number
        grade_bench_mark = self.grade_bench_mark.continous_grade
        try:
            if not self.continous_grade:
                self.student_course.continous_grade = None
            else:
                self.continous_grade = float(self.continous_grade)
                if self.continous_grade > grade_bench_mark:
                    raise CASBenchMarkError(student)
                elif self.continous_grade <= grade_bench_mark:
                    self.student_course.continous_grade = self.continous_grade
            self.student_course.save()
        except ValueError:
            pass
        except CASBenchMarkError as error:
            raise error
        
    def _save_endsemester_grade(self):
        student = self.student_course.enrollment.student_number
        grade_bench_mark = self.grade_bench_mark.endsemester_grade
        try:
            if not self.endsemester_grade:
                self.student_course.endsemester_grade = None
            else:
                self.endsemester_grade = float(self.endsemester_grade)
                if self.endsemester_grade and self.endsemester_grade > grade_bench_mark:
                    raise EOSBenchMarkError(student)
                elif self.endsemester_grade and self.endsemester_grade <= grade_bench_mark:
                    self.student_course.endsemester_grade = self.endsemester_grade
            self.student_course.save()
       
        except ValueError:
            pass
        except EOSBenchMarkError as error:
            raise error
         
    def _has_continous_grade(self):
        if self.student_course.continous_grade:
            return True
        else:
            return False

    def _has_endsemester_grade(self):
        if self.student_course.endsemester_grade:
            return True
        else:
            return False

    def _reset_final_grade(self):
        self.student_course.final_grade = None
        self.student_course.grade_point = None
        self.student_course.letter_grade = None
        self.student_course.save()

    def _set_final_grade(self):
        continous_grade = float(self.student_course.continous_grade)
        endsemester_grade = float(self.student_course.endsemester_grade)
        final_grade = (continous_grade + endsemester_grade)
        grade_scheme = self._get_grade_scheme(final_grade)

        self.student_course.final_grade = final_grade
        if grade_scheme:
            self.student_course.grade_point = grade_scheme.grade_point
            self.student_course.letter_grade = grade_scheme.letter_grade
        self.student_course.save()

    def _save_final_grade(self):
        if self._has_continous_grade() and self._has_endsemester_grade():
           self._set_final_grade()
        else:
            self._reset_final_grade()

    def set_course_attempt(self, course_attempt):
        self.student_course.course_attempt = course_attempt

    def process(self):
        self._save_continuous_grade()
        self._save_endsemester_grade()
        self._save_final_grade()

#### END GRADE ENTRY ####
        

### EXTENDED GRADE PROXY

class MissingGrade(object):
    
    def __init__(self, department) -> None:
        if isinstance(department, Department):
            self.department = department
        else:
            self.department = Department.objects.get(pk=department)
        
        if self.department:
            self.campus = self.department.faculty.campus

        self.grade_bench_mark = GradeBenchMark.get_active()
    
    def get_grades(self):
        return StudentCourse.objects.filter(
            course__department=self.department,
            final_grade=None,
            grade_point=None
        )
    

class SupplementaryGrade(MissingGrade):
    
    def get_grades(self):
        return Supplementary.objects.filter(
            course__department=self.department,
            status=SUPStatus.PENDING
        )

### END EXTENDED GRADE PROXY
 

#### ASSESSMENT #####
class CourseAssessment(object):

    def __init__(self, student_number, semester, academic_semester=None):
        self.student_number = student_number
        self.student = Student.get_by_student_number(student_number)
        self.enrollment = Enrollment.get_active(student_number)
        self.semester = semester
        self.program = self.enrollment.program
        self.passmark = self._get_pass_mark()

        if not academic_semester:
            self.academic_semester = self._get_academic_semester()
        else:
            if isinstance(academic_semester, AcademicSemester):
                self.academic_semester = academic_semester
            else:
                self.academic_semester = AcademicSemester.get_by_id(academic_semester)    

    def _get_academic_semester(self):
        if AcademicSemester.has_active(self.enrollment.campus):
            return AcademicSemester.get_active(self.enrollment.campus)
        else:
            return None

    def _get_pass_mark(self):
        program_type = self.enrollment.program.program_type
        return PassMark.get_by_program_type(program_type)

    def get_courses(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment
        )
    
    def get_semester_courses(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment,
            academic_semester=self.academic_semester,
            semester=self.semester
        )

    def get_failed_courses(self):
        course_types = [CourseType.CORE, CourseType.NONCORE]
        course_attempts = [CourseAttempt.NORMAL, CourseAttempt.CARRYOVER]
        return self.get_semester_courses().filter(
            course_attempt__in=course_attempts,
            course_type__in=course_types,
            final_grade__lt=self.passmark.pass_grade
        )

    def get_failed_core_courses(self):
        return self.get_semester_courses().filter(
            course_attempt=CourseAttempt.NORMAL,
            course_type=CourseType.CORE,
            final_grade__lt=self.passmark.pass_grade
        )
    
    def get_failed_nonecore_courses(self):
        return self.get_semester_courses().filter(
            course_attempt=CourseAttempt.NORMAL,
            course_type=CourseType.NONCORE,
            final_grade__lt=self.passmark.pass_grade
        )

    def get_failed_repeat_courses(self):
        return self.get_semester_courses().filter(
            course_attempt=CourseAttempt.REPEAT,
            final_grade__lt=self.passmark.pass_grade
        )
    
    def get_failed_sup_courses(self):
        return self.get_semester_courses().filter(
            course_attempt=CourseAttempt.SUP,
            course_type=CourseType.CORE,
            final_grade__lt=self.passmark.pass_grade
        )
    
    def get_failed_carryover_courses(self):
        return self.get_semester_courses().filter(
            course_attempt=CourseAttempt.CARRYOVER,
            course_type=CourseType.CORE,
            final_grade__lt=self.passmark.pass_grade
        )

    def get_missing_grades(self):
        return self.get_semester_courses().filter(
            final_grade=None,
            grade_point=None
        )

    def total_failed_courses(self):
        return self.get_failed_courses().count()

    def total_failed_core_courses(self):
        return self.get_failed_core_courses().count()
    
    def total_failed_nonecore_courses(self):
        return self.get_failed_nonecore_courses().count()

    def total_failed_sup_courses(self):
        return self.get_failed_sup_courses().count()

    def total_failed_carryover_courses(self):
        return self.get_failed_carryover_courses().count()

    def total_failed_repeat_courses(self):
        return self.get_failed_repeat_courses().count()

    def has_failed_course(self):
        return self.get_failed_courses().exists()

    def has_failed_core_course(self):
        return self.get_failed_core_courses().exists()

    def has_failed_sup_course(self):
        return self.get_failed_sup_courses().exists()

    def has_failed_carryover_course(self):
        return self.get_failed_carryover_courses().exists()

    def has_failed_repeat_course(self):
        return self.get_failed_repeat_courses().exists()

    def has_missing_grade(self):
        return self.get_missing_grades().exists()
    
    
class SemesterAssessment(CourseAssessment):
      
    def __init__(self, student_number, semester, academic_semester=None):
        super().__init__(student_number, semester, academic_semester)
        self.registration = self._get_registration()
        self.result = self._get_semester_result()
        self.assessment_version = AssessmentVersion.get_active()

    def _get_registration(self):
        return Registration.objects.filter(
            enrollment=self.enrollment,
            academic_semester=self.academic_semester,
            semester=self.semester
        ).first()

    def _get_semester_result(self) -> SemesterResult:
        return SemesterResult.objects.filter(
            enrollment=self.enrollment,
            academic_semester=self.academic_semester,
            semester=self.semester
        ).first()
    
    def _get_assessment_rule(self) -> AssessmentRule:
        assessment_version = self.assessment_version
        program_type = self.program.program_type
        cumulative_gpa = self.get_cumulative_gpa()
        is_first_year = self.is_first_year()
        is_repeating = self.is_repeating()
        has_failed_core = self.has_failed_core_course()
        has_failed_sup = self.has_failed_sup_course()
        has_failed_cov = self.has_failed_carryover_course()
        has_failed_rfc = self.has_failed_repeat_course()

        return AssessmentRule.objects.filter(
            program_type=program_type,
            min_cgpa__lte=cumulative_gpa,
            max_cgpa__gte=cumulative_gpa,
            is_first_year=is_first_year,
            is_repeating=is_repeating,
            has_failed_core=has_failed_core,
            has_failed_sup=has_failed_sup,
            has_failed_cov=has_failed_cov,
            has_failed_rfc=has_failed_rfc,
            assessment_version=assessment_version
        ).first()

    def _get_decision(self):
        decision = None
        if self.has_missing_grade():
            decision = ResultType.MGD
        else:
            assessment = self._get_assessment_rule()
            if not assessment:
                raise AssessmentRuleNotFoundException
            else:
                decision = assessment.decision
        return decision
   
    def _process_decision(self, decision):
        description = ResultDescription[decision]
        semester_gpa = self.get_semester_gpa()
        semester_credits = self.get_semester_credits() if semester_gpa else None
        cumulative_gpa = self.get_cumulative_gpa() if semester_gpa else None
        cumulative_credits = self.get_cumulative_credits() if semester_gpa else None
        
        result = self.result
        
        if not result:
            result = SemesterResult()
            result.enrollment=self.enrollment
            result.academic_semester=self.academic_semester
            result.semester=self.semester
            result.semester_gpa=semester_gpa
            result.semester_credits=semester_credits
            result.cumulative_gpa=cumulative_gpa
            result.cumulative_credits=cumulative_credits
            result.decision=decision
            result.description=description
            result.save()

        else:
            result.semester_gpa=semester_gpa
            result.semester_credits=semester_credits
            result.cumulative_gpa=cumulative_gpa
            result.cumulative_credits=cumulative_credits
            result.decision=decision
            result.description = description
            result.save()

        return result
   
    def get_semester_grade_points(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment,
            academic_semester=self.academic_semester,
            semester=self.semester
        ).aggregate(
            grade_points=Sum( F('grade_point') * F('course__credit_hours') ) 
        )['grade_points']       

    def get_semester_credits(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment,
            academic_semester=self.academic_semester,
            semester=self.semester
        ).aggregate(
            credit_hours=Sum('course__credit_hours')
        )['credit_hours']

    def get_cumulative_grade_points(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment,
            semester__lte=self.semester
        ).annotate(
            max_final_grade=Max('final_grade')
        ).distinct().aggregate(
            grade_points=Sum(F('grade_point') * F('course__credit_hours'))
        )['grade_points']

    def get_cumulative_credits(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment,
            semester__lte=self.semester
        ).distinct().aggregate(
            credit_hours=Sum('course__credit_hours')
        )['credit_hours']

    def get_semester_gpa(self):
        try:
            total_grade_points = self.get_semester_grade_points()
            total_credits = self.get_semester_credits()
            grade_point_average = (total_grade_points/total_credits)
            return round(grade_point_average, 2)
        except:
            pass

    def get_cumulative_gpa(self):
        try:
            total_grade_points = self.get_cumulative_grade_points()
            total_credits = self.get_cumulative_credits()
            grade_point_average = (total_grade_points/total_credits)
            return round(grade_point_average, 2)
        except:
            pass

    def is_repeating(self):
        return self.registration.is_repeat()

    def is_first_year(self):
        if self.registration.semester <= Settings.FIRST_YEAR_SEMESTERS:
            return True
        else:
            return False
  
    def process(self):
        decision = self._get_decision()
        result = self._process_decision(decision)
        progress = SemesterProgress(result)
        progress.process()
    

class ResultProcessor(ABC):

    def __init__(self, result: SemesterResult):
        self.result = result
        self.enrollment = result.enrollment
        self.semester = result.semester
        self.program = result.enrollment.program
    
    def _get_previous_semester(self):
        return self.semester - Settings.SEMESTER_INCREMENT

    def _get_previous_result(self) -> SemesterResult:
        previous_semester = self._get_previous_semester()
        return SemesterResult.objects.filter(
            enrollment=self.enrollment,
            semester=previous_semester
        ).first()


class SemesterProgress(ResultProcessor):
    
    def __init__(self, result: SemesterResult):
        super().__init__(result)
    
    def _get_registered_semesters(self):
        return Registration.objects.filter(enrollment=self.enrollment).count()
    
    def _is_overstaying(self):
        total_semesters = self._get_registered_semesters()
        semester_increment = total_semesters + Settings.SEMESTER_INCREMENT
        return semester_increment > self.program.max_semesters
        
    def _is_final_semester(self):
        return self.result.is_final_semester()
         
    def _increment_semester(self):
        enrollment = self.enrollment
        enrollment.semester = self.semester + Settings.SEMESTER_INCREMENT
        enrollment.save()

    def _can_compensate(self):
        try:
            result = self._get_previous_result()
            return result.is_pap() or result.is_pco()
        except:
            return False

    def _compensate(self):
        enrollment = self.enrollment
        enrollment.compensate()
        enrollment.graduating()
        enrollment.save()

    def _repeat_failed_course(self):
        decision = ResultType.RFC
        description = ResultDescription[decision]
        self.result.decision = decision
        self.result.description = description
        self.result.save()

    def _finish_studies(self):
        enrollment = self.enrollment
        enrollment.complete()
        enrollment.graduating()
        enrollment.save()

    def _process_award(self):
        try:
            award = AwardProcessor(self.result)
            award.process()
        except:
            pass

    def _academic_withdrawal(self):
        enrollment = self.enrollment
        enrollment.withdrawal()
        enrollment.save()
        try:
            withdrawal_type = WithdrawalType.get_academic()
            withdrawal = StudentWithdrawal(self.enrollment.student_number, withdrawal_type)
            withdrawal.process()
        except:
           pass

    def _fail_and_withdrawal(self):
        self.result.decision = ResultType.FAW
        self.result.save()

    def _readmit_withdrawal(self):
        if self.enrollment.is_withdrawal():
            self.enrollment.activate()
            self.enrollment.save()

    def _is_faw(self):
        return self.result.is_faw()
    
    def _is_pco(self):
        return self.result.is_pco()
    
    def _is_pap(self):
        return self.result.is_pap()

    def _process_pap(self):
        if not self._is_final_semester():
            if self._is_overstaying():
                self._fail_and_withdrawal()
            else:
                self._readmit_withdrawal()
                self._increment_semester()
        else:
            self._finish_studies()
            self._process_award()

    def _process_pco(self):
        if not self._is_final_semester():
            if self._is_overstaying():
                self._fail_and_withdrawal()
            else:
                self._readmit_withdrawal()
                self._increment_semester()
        else:
            self._repeat_failed_course()

    def _process_faw(self):
        if self._is_final_semester() and self._can_compensate():
            self._compensate()
            self._process_award()
        else:
            self._academic_withdrawal()
    
    def process(self):
        if self._is_pap():
            self._process_pap()
        elif self._is_pco():
           self._process_pco()
        elif self._is_faw():
            self._process_faw()
    

class AwardProcessor(ResultProcessor):

    def __init__(self, result: SemesterResult):
        super().__init__(result)
        self.assessment_version = AssessmentVersion.get_active()

    def _get_cumulative_grade_points(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment,
        ).annotate(
            max_final_grade=Max('final_grade')
        ).distinct().aggregate(
            grade_points=Sum(F('grade_point') * F('course__credit_hours'))
        )['grade_points']

    def _get_cumulative_credits(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment,
        ).distinct().aggregate(
            credit_hours=Sum('course__credit_hours')
        )['credit_hours']

    def _get_cumulative_gpa(self):
        try:
            total_grade_points = self._get_cumulative_grade_points()
            total_credits = self._get_cumulative_credits()
            grade_point_average = (total_grade_points/total_credits)
            return round(grade_point_average, 2)
        except:
            pass

    def _get_award_class(self):
        try:
            assessment_version = self.assessment_version
            program_type = self.enrollment.program.program_type
            cumulative_gpa = self._get_cumulative_gpa()
            repeated = self._has_repeat_record()
            
            award_scheme = AwardScheme.objects.filter(
                assessment_version=assessment_version,
                program_type=program_type,
                min_cgpa__lte=cumulative_gpa,
                max_cgpa__gte=cumulative_gpa,
                repeated=repeated,
            ).first()
            
            if award_scheme:
                return award_scheme.award_class
        except:
            pass
     
    def _get_pass_mark(self):
        program_type = self.enrollment.program.program_type
        return PassMark.get_by_program_type(program_type)

    def _can_certify(self):
        return self._has_program_credits() and self._has_passed()
   
    def _has_program_credits(self):
        cumulative_credits = self._get_cumulative_credits()
        program_credits = self._get_program_credits()
        return cumulative_credits >= program_credits

    def _has_passed(self):
        cumulative_gpa = self._get_cumulative_gpa()
        pass_mark = self._get_pass_mark()
        return cumulative_gpa >= pass_mark.pass_cgpa 

    def _has_repeat_record(self):
        return Registration.objects.filter(
            enrollment=self.enrollment,
            type=RegistrationType.REPEAT
        ).exists()

    def _get_program_credits(self):
        return MasterCurriculum.objects.filter(
            program=self.enrollment.program,
            semester__gte=self.enrollment.initial_semester
        ).distinct().aggregate(
            credit_hours=Sum('course__credit_hours')
        )['credit_hours']

    def _get_compensation_rule(self):
        program_level = self.program.program_level
        current_semester = self.semester
        previous_semester = self._get_previous_semester()
        previous_result = self._get_previous_result()

        return CompensationRule.objects.filter(
            program_level=program_level,
            withdrawal_semester=current_semester,
            previous_semester=previous_semester,
            previous_result=previous_result.decision
        ).first()

    def _get_compensatory_award(self, rule: CompensationRule, field_name: str):
        award_level = rule.award
        award_text =  award_level + " in " + field_name
        return award_text

    def _process_compensatory_award(self):
        try:
            rule = self._get_compensation_rule()
            field_name = self.program.field_name
            award_name = self._get_compensatory_award(rule, field_name)
            cumulative_gpa = self._get_cumulative_gpa()

            enrollment = self.enrollment
            enrollment.award_name = award_name
            enrollment.award_class = AwardScheme.DEFAULT_CLASS
            enrollment.award_level = rule.program_level
            enrollment.award_gpa = cumulative_gpa
            enrollment.certify()
            enrollment.save()
        except:
            pass

    def _process_standard_award(self):
        cumulative_gpa = self._get_cumulative_gpa()
        
        enrollment = self.enrollment
        enrollment.award_name = self.program.name
        enrollment.award_level = self.program.program_level
        enrollment.award_gpa = cumulative_gpa

        if self._can_certify():
            award_class = self._get_award_class()
            enrollment.award_class = award_class
            enrollment.certify()
        enrollment.save()

    def process(self):
        if self.result.is_pap():
            return self._process_standard_award()
        if self.result.is_faw():
            return self._process_compensatory_award()
        
#### END ASSESSMENT #####   


#### GRADE BOOK ####
class FacultyAssessment(object):

    def __init__(self, faculty, academic_semester=None) -> None:
        if isinstance(faculty, Faculty):
            self.faculty = faculty
        else:
            self.faculty = Faculty.get_by_id(faculty)
        
        if self.faculty:
            self.campus = self.faculty.campus

        if not academic_semester:
            self.academic_semester = self._get_academic_semester()
        else:
            if isinstance(academic_semester, AcademicSemester):
                self.academic_semester = academic_semester
            else:
                self.academic_semester = AcademicSemester.get_by_id(academic_semester)  

    def _get_academic_semester(self):
        if AcademicSemester.has_active(self.campus):
            return AcademicSemester.get_active(self.campus)
        else:
            return None
    
    def _get_max_semester(self):
        return Program.objects.annotate(Max('semesters')).distinct().first().semesters

    def _get_program_list(self):
        subquery = Registration.objects.filter(
            academic_semester=self.academic_semester,
            enrollment__program__department__faculty=self.faculty
        ).distinct().values_list('enrollment__program_id')

        return Program.objects.filter(id__in=subquery)
    
    def set_created_date(self, date):
        self.created_date = date

    def get_assessments(self):
        programs = self._get_program_list()
        semesters = self._get_max_semester()
        assessments = []
        for program in programs:
            for semester in range(1, semesters):
                assessment = ProgramAssessment(program, semester, self.academic_semester)
                if assessment.is_valid():
                    assessments.append(assessment)
        return assessments


class ProgramAssessment(object):
     
    def __init__(self, program, semester, academic_semester=None) -> None:
        self.semester = semester
        if isinstance(program, Program):
            self.program = program
        else:
            self.program = Program.get_by_id(program)

        if self.program:
            self.campus = self.program.department.faculty.campus

        if not academic_semester:
            self.academic_semester = self._get_academic_semester()
        else:
            if isinstance(academic_semester, AcademicSemester):
                self.academic_semester = academic_semester
            else:
                self.academic_semester = AcademicSemester.get_by_id(academic_semester)  

    def _get_academic_semester(self):
        if AcademicSemester.has_active(self.campus):
            return AcademicSemester.get_active(self.campus)
        else:
            return None

    def _get_registrations(self):
        return Registration.objects.filter(
            enrollment__program=self.program,
            academic_semester=self.academic_semester,
            semester=self.semester,
        )

    def _get_performance_class(self, name):
        mapping = {
            ResultType.PAP: PAPSummary.__name__,
            ResultType.PCO: PCOSummary.__name__,
            ResultType.SUP: SUPSummary.__name__,
            ResultType.RFC: RFCSummary.__name__,
            ResultType.FAW: FAWSummary.__name__,
            ResultType.MGD: MGDSummary.__name__
        }
        try:
            class_name = mapping.get(name, None)
            return getattr(sys.modules[__name__], class_name)
        except:
            pass

    def _semester_result_queryset(self):
        return SemesterResult.objects.filter(
            enrollment__program=self.program,
            academic_semester=self.academic_semester,
            semester=self.semester
        )  

    def is_valid(self):
        total_students = self.total_students()
        if total_students > 0:
            return True
        else:
            return False

    def total_male(self):
        return self._semester_result_queryset().filter(enrollment__student__gender='Male').count()

    def total_female(self):
        return self._semester_result_queryset().filter(enrollment__student__gender='Female').count()

    def male_percent(self):
        try:
            total = self.total_students()
            male = self.total_male()
            return round((male/total) * 100,2)
        except:
            pass

    def female_percent(self):
        try:
            total = self.total_students()
            female = self.total_female()
            return round((female/total) * 100, 2)
        except:
            pass

    def total_students(self):
        return self._semester_result_queryset().count()
    
    def total_average(self):
        try:
            male = self.total_male()
            female = self.total_female()
            return round( (male + female )/2, 2)
        except:
            pass

    def get_students(self):
        registrations = self._get_registrations()
        assessments = list()
        for registration in registrations:
            assessment = SemesterAssessment(
                student_number=registration.enrollment.student_number,
                semester=self.semester,
                academic_semester=self.academic_semester
            )
            assessments.append(assessment)
        return assessments

    def get_courses(self):
        curriculum = CurriculumManager(
            program=self.program,
            semester=self.semester,
            academic_semester=self.academic_semester
        )
        return curriculum.get_courses()
    
    def get_course_summary(self):
        program_courses = self.get_courses()
        course_summary = list()
        for program_course in program_courses:
            summary = CourseSummary(program_course, self.academic_semester)
            course_summary.append(summary)
        return course_summary
    
    def get_performance_summary(self):
        resulttypes = ResultType.names
        performance_summary = list()
        for name in resulttypes:
            class_name = self._get_performance_class(name)
            if class_name:
                instance = class_name(self.program, self.semester, self.academic_semester)
                performance_summary.append(instance)
        return performance_summary
        

class ProgramPerformance(ProgramAssessment):
    performance = None
    description = None

    def __init__(self, program, semester, academic_semester=None) -> None:
        super().__init__(program, semester, academic_semester)
    
    def total(self):
        return self._semester_result_queryset().filter(decision=self.performance).count()

    def male(self):
        return self._semester_result_queryset().filter(
            enrollment__student__gender='Male',
            decision=self.performance).count()

    def female(self):
        return self._semester_result_queryset().filter(
            enrollment__student__gender='Female',
            decision=self.performance).count()

    def male_percent(self):
        try:
            total = self.total_male()
            male = self.male()
            return round((male/total) * 100)
        except:
            pass

    def female_percent(self):
        try:
            total = self.total_female()
            female = self.female()
            return round((female/total) * 100)
        except:
            pass
    
    def average(self):
        try:
            male_percent = self.male_percent()
            female_percent = self.female_percent()
            return round( (male_percent + female_percent )/2)
        except:
            pass

    def __str__(self):
        return self.performance


class PAPSummary(ProgramPerformance):

    def __init__(self, program, semester, academic_semester=None) -> None:
        super().__init__(program, semester, academic_semester)
        self.performance = ResultType.PAP
        self.description = ResultDescription[self.performance]


class PCOSummary(ProgramPerformance):
    
    def __init__(self, program, semester, academic_semester=None) -> None:
        super().__init__(program, semester, academic_semester)
        self.performance = ResultType.PCO
        self.description = ResultDescription[self.performance]


class SUPSummary(ProgramPerformance):

    def __init__(self, program, semester, academic_semester=None) -> None:
        super().__init__(program, semester, academic_semester)
        self.performance = ResultType.SUP
        self.description = ResultDescription[self.performance]
    

class RFCSummary(ProgramPerformance):
    
    def __init__(self, program, semester, academic_semester=None) -> None:
        super().__init__(program, semester, academic_semester)
        self.performance = ResultType.RFC
        self.description = ResultDescription[self.performance]


class MGDSummary(ProgramPerformance):
    
    def __init__(self, program, semester, academic_semester=None) -> None:
        super().__init__(program, semester, academic_semester)
        self.performance = ResultType.MGD
        self.description = ResultDescription[self.performance]


class FAWSummary(ProgramPerformance):
    
    def __init__(self, program, semester, academic_semester=None) -> None:
        super().__init__(program, semester, academic_semester)
        self.performance = ResultType.FAW
        self.description = ResultDescription[self.performance]


class CourseSummary(object):
    
    def __init__(self, program_course: MasterCurriculum | ConfiguredCourse, academic_semester: AcademicSemester) -> None:
        if isinstance(program_course, MasterCurriculum):
            self.program = program_course.program
        elif isinstance(program_course, ConfiguredCourse):
            self.program = program_course.curriculum.program
        self.program_type = self.program.program_type
        self.course = program_course.course
        self.course_type = program_course.course_type
        self.semester = program_course.semester
        self.academic_semester=academic_semester
        self.passmark = self._get_pass_mark()
    
    def _get_pass_mark(self):
        return PassMark.get_by_program_type(self.program_type)
    
    def queryset(self):
        return StudentCourse.objects.filter(
            enrollment__program=self.program,
            course=self.course,
            course_type=self.course_type,
            academic_semester=self.academic_semester,
            semester=self.semester
        )

    def total_students(self):
        return self.queryset().count()

    def pass_total(self):
        return self.queryset().filter(final_grade__gte=self.passmark.pass_grade).count()

    def fail_total(self):
        return self.queryset().filter(final_grade__lt=self.passmark.pass_grade).count()

    def grade_A(self):
        return self.queryset().filter(letter_grade__icontains='A').count()

    def grade_B(self):
        return self.queryset().filter(letter_grade__icontains='B').count()
  
    def grade_C(self):
        return self.queryset().filter(letter_grade__icontains='C').count()
    
    def grade_D(self):
        return self.queryset().filter(letter_grade__icontains='D').count()
    
    def grade_F(self):
        return self.queryset().filter(letter_grade__icontains='F').count()


class GradeBookManager(object):
    
    def __init__(self, faculty, academic_semester) -> None:
        if isinstance(faculty, Faculty):
            self.faculty = faculty
        else:
            self.faculty = Faculty.get_by_id(faculty)
        
        if self.faculty:
            self.campus = self.faculty.campus

        if isinstance(academic_semester, AcademicSemester):
            self.academic_semester = academic_semester
        else:
            self.academic_semester = AcademicSemester.get_by_id(academic_semester)  

    def create(self):
        gradebook = GradeBook.objects.filter(
            faculty=self.faculty,
            academic_semester=self.academic_semester
        ).first()
        if not gradebook:
            gradebook = GradeBook()
            gradebook.faculty = self.faculty
            gradebook.academic_semester = self.academic_semester
        gradebook.save()
        return gradebook


class GradeBookBuilder(object):

    def __init__(self, gradebook: GradeBook):
        self.gradebook = gradebook

    def generate(self):
        
        try:
            self.gradebook.set_processing()
            self.gradebook.save()
            
            APP_NAME = SarisAssessmentConfig.name
            template = get_template_name("gradebook/pdf.html", APP_NAME)
            assessment = FacultyAssessment(self.gradebook.faculty, self.gradebook.academic_semester)
            assessment.set_created_date(self.gradebook.created_at)
            
            context = {"gradebook": assessment}
            
            pdf_in_memory = io.BytesIO()

            helpers.render_pdf(
                template=template,
                file_=pdf_in_memory,
                context=context,
            )

            self.gradebook.pdf_file = File(pdf_in_memory, f"{self.gradebook.pk}.pdf")
            self.gradebook.set_ready()
            self.gradebook.save()
        except Exception as e:
            self.gradebook.set_error(str(e))
            self.gradebook.save()

#### END GRADE BOOK ####


#### RESULTS ####
class ResultStatement(object):
    
    def __init__(self, enrollment, academic_semester=None) -> None:
        if isinstance(enrollment, Enrollment):
            self.enrollment=enrollment
        else:
            self.enrollment = Enrollment.get_by_id(enrollment)

        if not academic_semester:
            self.academic_semester = self._get_academic_semester()
        else:
            if isinstance(academic_semester, AcademicSemester):
                self.academic_semester = academic_semester
            else:
                self.academic_semester = AcademicSemester.get_by_id(academic_semester)  

        self.student_number = self.enrollment.student.student_number
        self.signatory = Signatory.university_registrar()

    def _get_academic_semester(self):
        if AcademicSemester.has_active(self.enrollment.campus):
            return AcademicSemester.get_active(self.enrollment.campus)

    def _get_registration(self):
        return Registration.objects.filter(
            enrollment=self.enrollment, 
            academic_semester=self.academic_semester
        ).first()
    
    def _get_registrations(self):
        return Registration.objects.filter(
            enrollment=self.enrollment
        ).order_by('created_at')
    
    def get_results(self):
        timestamps = SemesterResult.objects.filter(enrollment=self.enrollment).values('semester').annotate(max_timestamp=Max('created_at'))
        newer_records = SemesterResult.objects.filter(enrollment=self.enrollment, created_at__in=timestamps.values('max_timestamp'))
        return newer_records
    
    def get_assessments(self) -> List[SemesterAssessment]:
        assessments = list()
        registrations = self._get_registrations()
        for registration in registrations:
            assessment = SemesterAssessment(self.student_number, registration.semester, registration.academic_semester)
            assessments.append(assessment)
        return assessments
    
    def get_assessment(self) -> SemesterAssessment:
        registration = self._get_registration()
        if registration:
            assessment = SemesterAssessment(self.student_number, registration.semester, registration.academic_semester)
            return assessment

    def process(self):
        assessment = self.get_assessment()
        if assessment:
            return assessment.process()

    def publish(self):
        assessment = self.get_assessment()
        publisher = ResultPublisher(assessment.result)
        publisher.publish()
 
    def process_all(self):
        assessments = self.get_assessments()
        for assessment in assessments:
            assessment.process()

    def publish_all(self):
        assessments = self.get_assessments()
        for assessment in assessments:
            publisher = ResultPublisher(assessment.result)
            publisher.publish()


class AcademicTranscript(ResultStatement):

    def __init__(self, enrollment) -> None:
        super().__init__(enrollment)
        self.grade_bench_mark = GradeBenchMark.get_active()
        self.grade_scheme_version = GradeSchemeVersion.get_active()
        self.assessment_version = AssessmentVersion.get_active()
        self.grade_scheme = self._get_grade_scheme()
        self.award_scheme = self._get_award_scheme()
        self.assessment_codes = self._get_assessment_codes()
        self.cumulative_credits = self._get_cumulative_credits()
        self.cumulative_gpa = self._get_cumulative_gpa()
        self.completion_date = self._get_completion_date()
        self.signatory = Signatory.vice_chancellor()

    def _get_grade_scheme(self):
        try:
            return GradeScheme.objects.filter(grade_scheme_version=self.grade_scheme_version)
        except:
            pass

    def _get_award_scheme(self):
        try:
            return AwardScheme.objects.filter(assessment_version=self.assessment_version)    
        except:
            pass

    def _get_assessment_codes(self):
        codes = ResultType.choices
        definitions = list()
        for key, value in codes:
            definition = str(ResultDescription[key])
            definitions.append((key,definition))
        return definitions
    
    def _get_cumulative_grade_points(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment,
        ).annotate(
            max_final_grade=Max('final_grade')
        ).distinct().aggregate(
            grade_points=Sum(F('grade_point') * F('course__credit_hours'))
        )['grade_points']

    def _get_cumulative_credits(self):
        return StudentCourse.objects.filter(
            enrollment=self.enrollment,
        ).distinct().aggregate(
            credit_hours=Sum('course__credit_hours')
        )['credit_hours']

    def _get_cumulative_gpa(self):
        try:
            total_grade_points = self._get_cumulative_grade_points()
            total_credits = self._get_cumulative_credits()
            grade_point_average = (total_grade_points/total_credits)
            return round(grade_point_average, 2)
        except:
            pass
    
    def _get_completion_date(self):
        try:
            result = SemesterResult.objects.filter(enrollment=self.enrollment).latest('created_at')
            if result:
                return result.created_at.date
        except:
            pass


class ResultPublisher(object):
    
    def __init__(self, result) -> None:
        if isinstance(result, SemesterResult):
            self.result = result
        else:
            self.result = SemesterResult.get_by_id(result)

    def get_courses(self):
        enrollment = self.result.enrollment
        academic_semester = self.result.academic_semester
        semester = self.result.semester
        return StudentCourse.objects.filter(
            enrollment=enrollment,
            academic_semester=academic_semester,
            semester=semester
        )
    
    def publish(self):

        published = PublishedResult.objects.update_or_create(
            id=self.result.pk,
            defaults={
                "enrollment":self.result.enrollment,
                "academic_semester":self.result.academic_semester,
                "semester":self.result.semester,
                "semester_gpa":self.result.semester_gpa,
                "semester_credits":self.result.semester_credits,
                "cumulative_gpa":self.result.cumulative_gpa,
                "cumulative_credits":self.result.cumulative_credits,
                "decision":self.result.decision,
                "description":self.result.description
            }
        )
        if published:
            studentcourses = self.get_courses()
            for studentcourse in studentcourses:
                PublishedGrade.objects.update_or_create(
                    id=studentcourse.pk,
                    defaults={
                        "enrollment":studentcourse.enrollment,
                        "academic_semester":studentcourse.academic_semester,
                        "course":studentcourse.course,
                        "course_type":studentcourse.course_type,
                        "course_attempt":studentcourse.course_attempt,
                        "semester":studentcourse.semester,
                        "continous_grade":studentcourse.continous_grade,
                        "endsemester_grade":studentcourse.endsemester_grade,
                        "final_grade":studentcourse.final_grade,
                        "grade_point":studentcourse.grade_point,
                        "letter_grade":studentcourse.letter_grade,
                    }
                )


class ResultManager(object):

    def __init__(self, academic_semester):
        
        if isinstance(academic_semester, AcademicSemester):
            self.academic_semester = academic_semester
        else:
            self.academic_semester = AcademicSemester.get_by_id(academic_semester)

    def _get_registrations(self):
        return Registration.objects.filter(academic_semester=self.academic_semester)
    
    def _get_missing_grades(self):
        return SemesterResult.objects.filter(
            academic_semester=self.academic_semester, 
            decision=ResultType.MGD
        )

    def _get_assessment(self, registration: Registration) -> SemesterAssessment:
        student_number = registration.enrollment.student.student_number
        semester = registration.semester
        academic_semester = self.academic_semester
        assessment = SemesterAssessment(student_number, semester, academic_semester)
        return assessment

    def process(self):
        registrations = self._get_registrations()
        for registration in registrations:
            assessment = self._get_assessment(registration)
            assessment.process()

    def publish(self):
        registrations = self._get_registrations()
        for registration in registrations:
            assessment = self._get_assessment(registration)
            result = assessment.result
            publisher = ResultPublisher(result)
            publisher.publish()

    def process_missing_grades(self):
        results = self._get_missing_grades()
        for result in results:
            student_number = result.enrollment.student.student_number
            semester = result.semester
            academic_semester = self.academic_semester
            assessment = SemesterAssessment(student_number, semester, academic_semester)
            assessment.process()
    
#### END RESULTS ####
                 

#### SUPP AND APPEAL ####

class AppealGradeEntry(object):
    
    def __init__(self, course_instance, continous_grade, endsemester_grade):
        if isinstance(course_instance, CourseAppeal):
            self.course_instance = course_instance
        else:
            self.course_instance = CourseAppeal.get_by_id(course_instance)

        self.continous_grade = continous_grade
        self.endsemester_grade = endsemester_grade
        self.grade_bench_mark = GradeBenchMark.get_active()  

    def _save_continuous_grade(self):
        student = self.course_instance.enrollment.student_number
        grade_bench_mark = self.grade_bench_mark.continous_grade
        try:
            continous_grade = float(self.continous_grade)
            if continous_grade > grade_bench_mark:
                raise CASBenchMarkError(student)
            elif continous_grade <= grade_bench_mark:
                self.course_instance.continous_grade = continous_grade
            self.course_instance.save()
        except ValueError:
            pass
        except CASBenchMarkError as error:
            raise error
        
    def _save_endsemester_grade(self):
        student = self.course_instance.enrollment.student_number
        grade_bench_mark = self.grade_bench_mark.endsemester_grade
        try:
            endsemester_grade = float(self.endsemester_grade)
            if endsemester_grade > grade_bench_mark:
                raise EOSBenchMarkError(student)
            elif endsemester_grade <= grade_bench_mark:
                self.course_instance.endsemester_grade = endsemester_grade
            self.course_instance.save()
    
        except ValueError:
            pass
        except EOSBenchMarkError as error:
            raise error
         
    def _has_continous_grade(self):
        if self.course_instance.continous_grade:
            return True
        else:
            return False

    def _has_endsemester_grade(self):
        if self.course_instance.endsemester_grade:
            return True
        else:
            return False

    def _update_status(self):
        self.course_instance.status = AppealStatus.GRADED
        self.course_instance.save()

    def process(self):
        self._save_continuous_grade()
        self._save_endsemester_grade()
        self._update_status()


class SUPGradeEntry(object):
    
    def __init__(self, course_instance, endsemester_grade):
        if isinstance(course_instance, Supplementary):
            self.course_instance = course_instance
        else:
            self.course_instance = Supplementary.get_by_id(course_instance)

        self.endsemester_grade = endsemester_grade
        self.grade_bench_mark = GradeBenchMark.get_active()
        
    def _save_endsemester_grade(self):
        student = self.course_instance.enrollment.student_number
        grade_bench_mark = self.grade_bench_mark.endsemester_grade
        try:
            endsemester_grade = float(self.endsemester_grade)
            if endsemester_grade > grade_bench_mark:
                raise EOSBenchMarkError(student)
            elif endsemester_grade <= grade_bench_mark:
                self.course_instance.endsemester_grade = endsemester_grade
            self.course_instance.save()
    
        except ValueError:
            pass
        except EOSBenchMarkError as error:
            raise error

    def _update_status(self):
        self.course_instance.status = SUPStatus.GRADED
        self.course_instance.save()

    def process(self):
        self._save_endsemester_grade()
        self._update_status()


class GradeProcessor(ABC):

    def __init__(self, campus):
        
        if isinstance(campus, Campus):
            self.campus = campus
        else:
            self.campus = Campus.get_by_id(campus)

    def get_enrollments(self):
        return self.get_grades().distinct().values_list("enrollment", flat=True)
    
    def grades_exist(self) -> bool:
        return self.get_grades().exists()
    
    def grades_not_exist(self) -> bool:
        return not self.get_grades().exists()
    
    def _update_grades(self):
        grades = self.get_grades()
        for grade in grades:
            manager = GradeEntry(
                student_course=grade.pk, 
                continous_grade=grade.continous_grade, 
                endsemester_grade=grade.endsemester_grade
            )
            manager.set_course_attempt(grade.course_attempt)
            manager.process()

    def _process_grades(self):
        enrollments = self.get_enrollments()
        for enrollment in enrollments:
            statement = ResultStatement(enrollment)
            statement.process_all()
    
    def _publish_grades(self):
        enrollments = self.get_enrollments()
        for enrollment in enrollments:
            statement = ResultStatement(enrollment)
            statement.publish_all() 
    
    def process(self):
        self._update_grades()
        self._process_grades()

    def publish(self):
        self._publish_grades()

    @abstractmethod
    def get_grades(self):
        pass
    
  
class AppealGradeManager(GradeProcessor):
    
    def _update_status(self):
        grades = self.get_grades()
        for grade in grades:
            grade.status = AppealStatus.RESOLVED
            grade.save()

    def get_grades(self):
        return CourseAppeal.objects.filter(
            enrollment__campus=self.campus,
            status=AppealStatus.GRADED
        )
    
    def check_appeals(self):
        if self.grades_not_exist():
            raise CourseAppealsNotFoundException

    def publish(self):
        self._publish_grades()
        self._update_status()


class SUPGradeManager(GradeProcessor):

    def get_grades(self):
        return Supplementary.objects.filter(
            enrollment__campus=self.campus,
            status=SUPStatus.GRADED
        )
    
    def check_supplementary(self):
        if self.grades_not_exist():
            raise SupplementaryNotFoundException


### END SUPP AND APPEAL