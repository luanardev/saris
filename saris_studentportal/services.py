
from abc import ABC, abstractmethod
from account.services import Signatory
from saris_admission.models import Enrollment
from saris_assessment.exceptions import ExamResultsNotFoundException, SupplementaryNotFoundException
from saris_assessment.models import AppealStatus, AppealType, CourseAppeal, PublishedGrade, PublishedResult, Supplementary
from saris_assessment.services import SemesterAssessment
from saris_billing.services import InvoiceTracker, RemarkInvoice
from saris_billing.exceptions import BalanceException
from saris_calendar.models import AcademicSemester
from saris_registration.models import Registration
from saris_registration.services import RegistrationManager, RegisterPolicy
from saris_studentportal.exceptions import ResultStatementNotFoundException
from saris_students.models import Student



class BaseProcessor(ABC):

    def __init__(self, student_number,  academic_semester = None):
        self.student_number = student_number
        self.student = Student.get_by_student_number(student_number)
        self.enrollment = Enrollment.get_active(student_number)
        self.program = self.enrollment.program
        self.campus = self.enrollment.campus

        if not academic_semester:
            self.academic_semester = self.get_academic_semester()
        elif isinstance(academic_semester, AcademicSemester):
            self.academic_semester = academic_semester
        else:
            self.academic_semester = AcademicSemester.get_by_id(academic_semester)   

        self.previous_academic_semester = AcademicSemester.get_previous(self.campus)

        self.semester = self.enrollment.semester

        self.registration = RegistrationManager(self.student_number, self.academic_semester)

    def get_academic_semester(self):
        if not self.campus:
            return None
        elif AcademicSemester.has_active(self.campus):
            return AcademicSemester.get_active(self.campus)
        else:
            return None
     
    def get_register(self):
        return self.registration.get_register()
    
    @abstractmethod
    def process(self):
        pass


class StudentRegistration(BaseProcessor):

    def __init__(self, student_number, academic_semester = None):
        super().__init__(student_number, academic_semester)
        self._policy = RegisterPolicy(self.campus)
        self._invoice_tracker = InvoiceTracker(self.student_number)
        
    def should_block(self):
        return self._policy.should_block_registration()
   
    def get_registration(self):
        return self.get_register().get_registration()
    
    def check_registration(self):
        return self.get_register().check_registration()
    
    def check_withdrawal(self):
        return self.get_register().check_withdrawal()
    
    def check_completion(self):
        return self.get_register().check_completion()
    
    def process(self):
        return self.get_register().process()


class ExamPermit(StudentRegistration):

    def __init__(self, student_number, academic_semester = None):
        super().__init__(student_number, academic_semester)
        self.invoice_tracker = InvoiceTracker(student_number)
        self.signatory = self.get_signatory()
        self.qrcode_info = self.get_qrcode_info()   
        self.semester = self._get_semester() 
   
    def _get_semester(self):
        registration = self.get_registration()
        if registration:
            return registration.semester 

    def get_signatory(self):
        signatory = Signatory.university_registrar()
        return signatory
    
    def get_qrcode_info(self):
        data = f'''
            StudentNumber: {self.student.student_number}, 
            StudentName: {self.student}, 
            Programme: {self.program.code},
            Semester: {self.semester},
            Session: {self.academic_semester},
            Balance: {self.invoice_tracker.get_total_balance()},
            Status: Permitted
        '''
        return data

    def should_block(self):
        return self._policy.should_block_examination()
        
    def get_courses(self):
        registration = self.get_registration()
        return registration.get_courses()
            
    def process(self):
        if self.should_block():
            if self.invoice_tracker.has_outstanding_balance():
                raise BalanceException
    
        
class ResultsAccess(ExamPermit):

    def should_block(self):
        return self._policy.should_block_results()
    
    def get_summary(self):
        registration = self.get_registration()
        results = PublishedResult.objects.get(
            enrollment=registration.enrollment,
            semester=registration.semester,
            academic_semester=registration.academic_semester
        )
        return results  

    def get_grades(self):
        registration = self.get_registration()
        results = PublishedGrade.objects.filter(
            enrollment=registration.enrollment,
            semester=registration.semester,
            academic_semester=registration.academic_semester
        )
        return results 

    def has_grades(self):
        return self.get_grades().exists()     
    
    def has_no_grades(self):
        return not self.has_grades()
    
    def check_results(self):
        if self.has_no_grades():
            raise ExamResultsNotFoundException

    def _get_appeal_pks(self):
        registration = self.get_registration()
        appeals = CourseAppeal.objects.filter(
            enrollment=registration.enrollment,
            academic_semester=registration.academic_semester,
            semester=registration.semester
        ).values_list("id", flat=True)
        return appeals

    def get_grades_without_appeal(self):
        appeals = self._get_appeal_pks()
        return self.get_grades().exclude(pk__in=appeals)


class StudentStatement(ExamPermit):

    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)

    def _result_published(self):
        return PublishedResult.objects.filter(enrollment=self.enrollment,academic_semester=self.academic_semester).exists()
    
    def _has_balance(self):
        return self.invoice_tracker.has_outstanding_balance()

    def get_registrations(self):
        registrations = Registration.objects.filter(
            enrollment=self.enrollment
        )
        published = self._result_published()
        has_balance = self._has_balance()

        if not published or has_balance:
            registrations = registrations.exclude(academic_semester=self.academic_semester)

        return registrations.order_by('created_at')
    
    def get_assessments(self):
        assessments = list()
        registrations = self.get_registrations()
        for registration in registrations:
            assessment = SemesterAssessment(self.student_number, registration.semester, registration.academic_semester)
            assessments.append(assessment)
        return assessments
    
    def check_statement(self):
        if not self.has_results():
            raise ResultStatementNotFoundException
    
    def has_results(self):
        elements = self.get_assessments()
        if len(elements) > 0:
            return True
        else:
            return False
    

class StudentAppeal(BaseProcessor):

    def __init__(self, student_number) -> None:
        super().__init__(student_number)
        self.student_number = student_number
        self._courses = list()

    def _create_appeal(self, publishedgrade: PublishedGrade):
        appeal_type = self.get_appeal_type()
        appeal_status = AppealStatus.PENDING

        CourseAppeal.objects.update_or_create(
            id=publishedgrade.pk,
            enrollment=publishedgrade.enrollment,
            academic_semester=publishedgrade.academic_semester,
            course=publishedgrade.course,
            course_type=publishedgrade.course_type,
            course_attempt=publishedgrade.course_attempt,
            semester=publishedgrade.semester,
            old_continous_grade=publishedgrade.continous_grade,
            old_endsemester_grade=publishedgrade.endsemester_grade,
            appeal_type=appeal_type,
            status=appeal_status
        )

    def set_course(self, course: any):
        if not isinstance(course, PublishedGrade):
            course = PublishedGrade.get_by_id(course)
        if not course in self._courses:
            self._courses.append(course)

    def set_courses(self, courses: list):
        for course in courses:
            self.set_course(course)

    def get_courses(self):
        return self._courses

    def count(self):
        return len(self._courses)

    def process(self):
        for course in self._courses:
            self._create_appeal(course)
    
    @abstractmethod
    def get_appeal_type(self):
        pass


class CourseRemark(StudentAppeal):

    def get_appeal_type(self):
        return AppealType.COURSE_REMARK
    
    def invoice_manager(self):
        quantity = self.count()
        invoice_manager = RemarkInvoice(self.student_number)
        invoice_manager.set_quantity(quantity)
        return invoice_manager
     
    def create_invoice(self):
        invoice_manager = self.invoice_manager()
        return invoice_manager.create()
    
    def preview_invoice(self):
        invoice_manager = self.invoice_manager()
        return invoice_manager.preview()

    def _process_invoice(self):
        invoice_manager = self.invoice_manager()
        invoice_manager.create()
        return invoice_manager.process()   
    
    def cancel(self):
        return self.invoice_manager().cancel()

    def process(self):
        self._process_invoice()
        return super().process()


class GradeCorrection(StudentAppeal):

    def get_appeal_type(self):
        return AppealType.GRADE_CORRECTION
    

class StudentSupplementary(BaseProcessor):
   
    def check_supplementary(self):
        result = self.registration.get_current_result()
        if not result.is_sup() and not result.is_sup_and_rfc():
            raise SupplementaryNotFoundException
    
    def get_courses(self):
          return Supplementary.objects.filter(
            enrollment=self.enrollment,
            academic_semester=self.academic_semester,
            semester=self.semester
        )

    def process(self):
        pass