from abc import ABC, abstractmethod
from saris_admission.models import Enrollment
from saris_assessment.services import SemesterAssessment
from saris_assessment.models import CourseAttempt, StudentCourse, Supplementary
from saris_billing.models import Invoice
from saris_billing.services import BaseInvoice, InvoicePayment, RFCInvoice, SUPInvoice, TuitionInvoice
from saris_calendar.models import AcademicSemester
from saris_curriculum.models import MasterCurriculum
from saris_curriculum.services import CurriculumManager
from saris_students.models import Student
from .exceptions import (
    AlreadyRegisteredException,
    DeregistrationException, 
    FailAndWithdrawalException, 
    RegistrationNotFoundException,
)
from .models import (
    Registration, 
    RegistrationStatus, 
    RegistrationPolicy,
    RegistrationType
)


class BaseProcessor(ABC):
    SEMESTER_INCREMENT = 1

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

    def get_academic_semester(self):
        if not self.campus:
            return None
        elif AcademicSemester.has_active(self.campus):
            return AcademicSemester.get_active(self.campus)
        else:
            return None
    
    def get_current_semester_assessment(self, semester):
        return SemesterAssessment(self.student_number, semester, self.academic_semester)
    
    def get_previous_semester_assessment(self, semester):
        return SemesterAssessment(self.student_number, semester, self.previous_academic_semester)
    
    def get_previous_study_semester(self) -> int:
        return int(self.semester - self.SEMESTER_INCREMENT)
    

class RegisterPolicy(object):
    
    def __init__(self, campus) -> None:
        self.policy = self._get_policy(campus)

    def _get_policy(self, campus):
        return RegistrationPolicy.get_by_campus(campus)

    def get_registration_installment(self):
        return self.policy.registration_installment
    
    def get_examination_installment(self):
        return self.policy.examination_installment
    
    def get_results_installment(self):
        return self.policy.results_installment
    
    def should_block_registration(self):
        return self.policy.block_registration
    
    def should_block_examination(self):
        return self.policy.block_examination
    
    def should_block_results(self):
        return self.policy.block_results
      
   
class BaseRegister(BaseProcessor):
    
    def __init__(self, student_number: int, academic_semester: AcademicSemester = None):
        super().__init__(student_number, academic_semester)

        self.curriculum_manager = CurriculumManager(
            program=self.program, 
            semester=self.semester, 
            academic_semester=self.academic_semester
        )
     
    def _queryset(self):
        return Registration.objects.filter(
            enrollment=self.enrollment, 
            academic_semester=self.academic_semester
        )

    def create_invoice(self):
        invoice = self.get_invoice_manager()
        return invoice.create()
    
    def cancel_invoice(self):
        invoice = self.get_invoice_manager()
        return invoice.cancel()

    def process_invoice(self):
        invoice = self.get_invoice_manager()
        return invoice.process()
    
    def pre_check_payment(self):
        invoice = self.get_invoice_manager()
        return invoice.pre_check_payment()
    
    def set_invoice_manager(self, invoice_manager: BaseInvoice):
        self.invoice_manager = invoice_manager
    
    def get_invoice_manager(self) -> BaseInvoice:
        quantity = self.item_count()
        self.invoice_manager.set_quantity(quantity)
        return self.invoice_manager
       
    def check_registration(self):
        if not self.has_registered():
            raise RegistrationNotFoundException
        
    def check_duplicate(self):
        if self.is_registered():
            raise AlreadyRegisteredException

    def check_withdrawal(self):
        return self.enrollment.check_withdrawal()

    def check_completion(self):
        return self.enrollment.check_completion()

    def get_registration(self) -> Registration:
        registration = self._queryset().first()
        return registration
    
    def is_registered(self) -> bool:
        type = self.get_type()
        return self._queryset().filter(semester=self.semester, type=type).exists()

    def has_registered(self):
        return self._queryset().exists()

    def is_new(self) -> bool:
        exists = Registration.objects.filter(enrollment=self.enrollment).exists()
        if not exists:
            return True
        else:
            return False

    def item_count(self):
        return 1

    def process(self):
        self.check_duplicate()

        self.pre_check_payment()

        self.create_invoice()

        self.process_invoice()

        registration = self.register()
        if registration:
            self.assign_courses()
        return registration
    
    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    def assign_courses(self):  
        pass


class StandardRegister(BaseRegister):
    
    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester) 
        self.policy = RegisterPolicy(self.campus)  
    
    def set_invoice_manager(self, invoice_manager: TuitionInvoice):
        return super().set_invoice_manager(invoice_manager)
    
    def get_invoice_manager(self) -> BaseInvoice:
        quantity = self.item_count()
        installment_percent = self.policy.get_registration_installment()
        self.invoice_manager.set_quantity(quantity)
        self.invoice_manager.set_installment_percent(installment_percent)
        return self.invoice_manager

    def get_type(self):
        return RegistrationType.NORMAL

    def check_curriculum(self):
        return self.curriculum_manager.check_master_curriculum()

    def register(self):
        registration = Registration()
        registration.academic_semester = self.academic_semester
        registration.enrollment = self.enrollment
        registration.semester = self.semester
        registration.type = RegistrationType.NORMAL
        registration.status = RegistrationStatus.REGISTERED
        registration.save()
        return registration
           
    def assign_courses(self):  
        courses = self.curriculum_manager.get_courses()
           
        for instance in courses:
            student_course = StudentCourse()
            student_course.academic_semester = self.academic_semester
            student_course.enrollment = self.enrollment
            student_course.semester = self.semester
            student_course.course = instance.course
            student_course.course_type = instance.course_type
            student_course.course_attempt = CourseAttempt.NORMAL
            student_course.save()

    def pre_check_payment(self):
        if self.policy.should_block_registration():
            super().pre_check_payment()

    def process(self):
        self.check_duplicate()
        self.check_curriculum()

        self.pre_check_payment()
        self.create_invoice()
        self.process_invoice()

        registration = self.register()
        if registration:
            self.assign_courses()
        return registration
        
     
class PAPRegister(StandardRegister):
    
    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)


class PCORegister(StandardRegister):

    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)

    def get_failed_courses(self):
        semester = self.get_previous_study_semester()
        assessment = self.get_previous_semester_assessment(semester)
        if assessment.has_failed_sup_course():
            return assessment.get_failed_sup_courses()

    def assign_courses(self):
        super().assign_courses()
        courses = self.get_failed_courses()
        if courses:
            for instance in courses:
                student_course = StudentCourse()
                student_course.academic_semester = self.academic_semester
                student_course.enrollment = self.enrollment
                student_course.semester = self.semester
                student_course.course = instance.course
                student_course.course_type = instance.course_type
                student_course.course_attempt = CourseAttempt.CARRYOVER
                student_course.save()

  
class SUPRegister(BaseRegister):
    
    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)
    
    def set_invoice_manager(self, invoice_manager: SUPInvoice):
        return super().set_invoice_manager(invoice_manager)
    
    def register(self):
        registration = self.get_registration()
        registration.type = RegistrationType.SUP
        registration.save()
        return registration
     
    def item_count(self):
        count = 0
        assessment = self.get_current_semester_assessment(self.semester)
        if assessment.has_failed_core_course():
            count = assessment.total_failed_core_courses()
        return count
    
    def get_failed_courses(self):
        assessment = self.get_current_semester_assessment(self.semester)
        if assessment.has_failed_core_course():
            return assessment.get_failed_core_courses()
    
    def get_type(self):
        return RegistrationType.SUP

    def assign_courses(self):
        courses = self.get_failed_courses()
        if courses:
            for instance in courses:
                Supplementary.objects.update_or_create(
                    id=instance.pk,
                    defaults={
                        "enrollment":instance.enrollment,
                        "academic_semester":instance.academic_semester,
                        "course":instance.course,
                        "course_type":instance.course_type,
                        "course_attempt":CourseAttempt.SUP,
                        "semester":instance.semester,
                        "continous_grade":instance.continous_grade,
                        "endsemester_grade":None
                    }
                )     


class RFCRegister(BaseRegister):
    
    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)
     
    def set_invoice_manager(self, invoice_manager: RFCInvoice):
        return super().set_invoice_manager(invoice_manager) 
        
    def is_final_semester(self):
        return self.semester == self.program.semesters

    def register(self):
        registration = Registration()
        registration.academic_semester = self.academic_semester
        registration.enrollment = self.enrollment
        registration.semester = self.semester
        registration.type = RegistrationType.REPEAT
        registration.status = RegistrationStatus.REGISTERED
        registration.save()
        return registration
    
    def item_count(self):
        count = 0
        assessment = self.get_previous_semester_assessment(self.semester)
        if assessment.has_failed_core_course():
            count = assessment.total_failed_core_courses()
        elif assessment.has_failed_carryover_course():
            count = assessment.total_failed_carryover_courses()
        elif self.is_final_semester():
            count = assessment.total_failed_sup_courses()
        return count
         
    def get_failed_courses(self):
        assessment = self.get_previous_semester_assessment(self.semester)
        if assessment.has_failed_course(): 
            return assessment.get_failed_courses()
        elif assessment.has_failed_carryover_course():
            return assessment.get_failed_carryover_courses()
        elif self.is_final_semester():
            return assessment.get_failed_sup_courses()
    
    def get_type(self):
        return RegistrationType.REPEAT

    def assign_courses(self):
        courses = self.get_failed_courses()
        if courses:
            for instance in courses:
                student_course = StudentCourse()
                student_course.academic_semester = self.academic_semester
                student_course.enrollment = self.enrollment
                student_course.semester = self.semester
                student_course.course = instance.course
                student_course.course_type = instance.course_type
                student_course.course_attempt = CourseAttempt.REPEAT
                student_course.save()


class RFCPlusRegister(RFCRegister):
    
    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)
    
    def get_failed_courses(self): 
        assessment = self.get_previous_semester_assessment(self.semester)
        return assessment.get_failed_carryover_courses()


class RegistrationManager(BaseProcessor):
     
    def __init__(self, student_number, academic_semester = None):
        super().__init__(student_number, academic_semester)
        self.policy = RegisterPolicy(self.campus)

    def get_previous_result(self):
        semester = self.get_previous_study_semester()
        assessment = self.get_previous_semester_assessment(semester)
        return assessment.result
    
    def get_current_result(self):
        assessment = self.get_current_semester_assessment(self.semester)
        return assessment.result

    def _create_register(self, invoice_manager, processor_class) -> BaseRegister:
        processor = processor_class(self.student_number)
        processor.set_invoice_manager(invoice_manager)
        return processor

    def get_register(self) -> BaseRegister:
        invoice_manager = TuitionInvoice(self.student_number)

        previous_result = self.get_previous_result()
        current_result = self.get_current_result()
        
        if previous_result and previous_result.is_faw():
            raise FailAndWithdrawalException

        elif current_result and current_result.is_sup():
            invoice_manager = SUPInvoice(self.student_number)
            return self._create_register(invoice_manager, SUPRegister)
        
        elif current_result and current_result.is_sup_and_rfc():
            invoice_manager = SUPInvoice(self.student_number)
            return self._create_register(invoice_manager, SUPRegister)

        elif previous_result and previous_result.is_rfc():
            invoice_manager = RFCInvoice(self.student_number)
            return self._create_register(invoice_manager, RFCRegister)

        elif previous_result and previous_result.is_rfc_and_pco():
            invoice_manager = RFCInvoice(self.student_number)
            return self._create_register(invoice_manager, RFCPlusRegister)
        
        elif previous_result and previous_result.is_rfc_and_rfc():
            invoice_manager = RFCInvoice(self.student_number)
            return self._create_register(invoice_manager, RFCPlusRegister)
        
        elif previous_result and previous_result.is_pco():
            return self._create_register(invoice_manager, PCORegister)

        elif previous_result and previous_result.is_pap():
            return self._create_register(invoice_manager, PAPRegister)

        else:
            return self._create_register(invoice_manager, StandardRegister)
   

class DeregistrationManager(BaseProcessor):
    
    def __init__(self, registration: Registration) -> None:
        self.registration = registration
        student_number = registration.enrollment.student.student_number
        academic_semester = registration.academic_semester
        super().__init__(student_number, academic_semester)
      
    def check_grades(self):
        has_grades = self.registration.has_graded_courses()
        if has_grades:
            raise DeregistrationException
     
    def get_invoice(self) -> Invoice:
        invoice = None
        
        if self.registration.is_normal():
            invoice = TuitionInvoice(self.student_number)
        if self.registration.is_repeat():
            invoice =  RFCInvoice(self.student_number)
        if self.registration.is_sup():
            invoice = SUPInvoice(self.student_number)

        service = invoice.get_service()
        enrollment = self.enrollment
        academic_semester = self.academic_semester

        invoice = Invoice.objects.filter(
            enrollment=enrollment,
            academic_semester=academic_semester,
            service=service).first()
        return invoice

    def cancel_invoice(self):
        invoice = self.get_invoice()
        if invoice:
            manager = InvoicePayment(invoice)
            manager.cancel_invoice()
    
    def process(self):
        self.check_grades()
        self.cancel_invoice()
        self.registration.delete_courses()
        self.registration.delete()
  
  
class RegisterCourseManager(object):
    
    def __init__(self, registration, curriculum_course, course_attempt):
        if isinstance(registration, Registration):
            self.registration = registration
        else:
            self.registration = Registration.get_by_id(registration)
        
        if isinstance(curriculum_course, MasterCurriculum):
            self.curriculum_course = curriculum_course
        else:
            self.curriculum_course = MasterCurriculum.get_by_id(curriculum_course)
        self.course_attempt = course_attempt
              
    def process(self):
        student_course = StudentCourse()
        student_course.course = self.curriculum_course.course
        student_course.course_type = self.curriculum_course.course_type
        student_course.course_attempt = self.course_attempt
        student_course.academic_semester = self.registration.academic_semester
        student_course.enrollment = self.registration.enrollment
        student_course.semester = self.registration.semester 
        student_course.save()
                 

class DeregisterCourseManager(object):

    def __init__(self, student_course):
        if isinstance(student_course, StudentCourse):
            self.student_course = student_course
        else:
            self.student_course = StudentCourse.get_by_id(student_course)
        
    def process(self):
        if self.student_course.is_graded():
            raise DeregistrationException
        self.student_course.delete()


class DeregisterCourseListManager(object):

    def __init__(self, student_courses: list):
        self.student_courses = student_courses

    def process(self):
        for student_course in self.student_courses:
            manager = DeregisterCourseManager(student_course)
            manager.process()

     
