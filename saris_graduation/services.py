import io
from django_renderpdf import helpers
from django.core.files import File
from saris.utils import get_template_name
from saris_admission.models import Enrollment, EnrollmentStatus
from saris_assessment.models import AssessmentVersion, AwardScheme
from saris_curriculum.models import Program
from saris_institution.models import Campus
from .models import Booklet, Candidate, Session
from .apps import SarisGraduationConfig
from .exceptions import CandidatesNotFoundException, GraduandsNotFoundException


class CandidatesManager(object):

    def __init__(self, session, campus):
        if isinstance(session, Session):
            self.session = session
        else:
            self.session = Session.get_by_id(session)

        if isinstance(campus, Campus):
            self.campus = campus
        else:
            self.campus = Campus.get_by_id(campus)

    def _get_completed(self):
        return Enrollment.objects.filter(
            campus=self.campus,
            status=EnrollmentStatus.COMPLETED,
            is_graduating=True,
            is_certified=True 
        )
    
    def has_candidates(self):
        return Enrollment.objects.filter(
            campus=self.campus,
            status=EnrollmentStatus.COMPLETED,
            is_graduating=True,
            is_certified=True 
        ).exists()

    def check_candidates(self):
        if not self.has_candidates():
            raise CandidatesNotFoundException

    def get_candidates(self):
        return Candidate.objects.filter(
            session = self.session,
            enrollment__campus = self.campus
        )

    def process(self):
        self.check_candidates()
        enrollments = self._get_completed()
        for enrollment in enrollments:
            candidate = Candidate()
            candidate.enrollment = enrollment
            candidate.session = self.session
            candidate.save()
            enrollment.graduate()
            enrollment.save()


class BookletManager(object):
    
    def __init__(self, session):
        if isinstance(session, Session):
            self.session = session
        else:
            self.session = Session.get_by_id(session)

    def has_graduands(self):
        return Candidate.objects.filter(
            session = self.session
        ).exists()

    def check_graduands(self):
        if not self.has_graduands():
            raise GraduandsNotFoundException

    def create(self):
        booklet = Booklet.objects.filter(
            session=self.session
        ).first()
        if not booklet:
            booklet = Booklet()
            booklet.session = self.session
        booklet.save()
        return booklet


class BookletBuilder(object):

    def __init__(self, booklet: Booklet):
        self.booklet = booklet

    def generate(self):
        
        try:
            self.booklet.set_processing()
            self.booklet.save()

            APP_NAME = SarisGraduationConfig.name
            template = get_template_name("booklet/pdf.html", APP_NAME)
            booklet = GraduationBooklet(self.booklet.session)
            booklet.set_created_date(self.booklet.created_at)
            
            context = {"booklet": booklet}
            
            pdf_in_memory = io.BytesIO()

            helpers.render_pdf(
                template=template,
                file_=pdf_in_memory,
                context=context,
            )

            self.booklet.pdf_file = File(pdf_in_memory, f"{self.booklet.pk}.pdf")
            self.booklet.set_ready()
            self.booklet.save()
        except Exception as e:
            self.booklet.set_error(str(e))
            self.booklet.save()


class GraduationBooklet(object):

    def __init__(self, session) -> None:
        self.session = session

    def set_created_date(self, date):
        self.created_date = date

    def get_program_list(self):
        subquery = Candidate.objects.filter(
            session=self.session
        ).distinct().values_list('enrollment__program_id')

        return Program.objects.filter(id__in=subquery)

    def get_program_booklets(self):
        programs = self.get_program_list()
        booklets = []
        for program in programs:
            booklet = ProgramBooklet(program, self.session)
            booklets.append(booklet)
        return booklets
    
    def get_total_male(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__student__gender="Male"
        ).count()

    def get_total_female(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__student__gender="Female"
        ).count()

    def get_total_candidates(self):
        return Candidate.objects.filter(
            session=self.session
        ).count()


class ProgramBooklet(object):
    
    def __init__(self, program, session):
        if isinstance(program, Program):
            self.program = program
        else:
            self.program = Program.get_by_id(program)
        
        if isinstance(session, Session):
            self.session = session
        else:
            self.session = Session.get_by_id(session)

        self.assessment_version = AssessmentVersion.get_active()

    def _get_award_class_list(self):
        return AwardScheme.objects.filter(
            assessment_version=self.assessment_version
        ).distinct().values_list('award_class', flat=True)

    def get_performance(self):
        award_class_list =  self._get_award_class_list()
        performances = []
        for award_class in award_class_list:
            performance = ProgramPerformance(self.program, self.session, award_class)
            performances.append(performance)
        return performances

    def get_candidates(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__program=self.program,
            enrollment__is_compensated=False
        ).order_by('-enrollment__award_gpa')
    
    def get_compensations(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__program=self.program,
            enrollment__is_compensated=True
        )

    def get_total_male(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__program=self.program,
            enrollment__student__gender="Male"
        ).count()

    def get_total_female(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__program=self.program,
            enrollment__student__gender="Female"
        ).count()

    def get_total_candidates(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__program=self.program
        ).count()


class ProgramPerformance(object):

    def __init__(self, program, session, award_class):
        self.program = program
        self.session = session
        self.award_class = award_class

    def get_candidates(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__program=self.program,
            enrollment__award_class=self.award_class
        )

    def get_total_male(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__program=self.program,
            enrollment__award_class=self.award_class,
            enrollment__student__gender="Male"
        ).count()

    def get_total_female(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__program=self.program,
            enrollment__award_class=self.award_class,
            enrollment__student__gender="Female"
        ).count()

    def get_total_candidates(self):
        return Candidate.objects.filter(
            session=self.session,
            enrollment__program=self.program,
            enrollment__award_class=self.award_class
        ).count()
