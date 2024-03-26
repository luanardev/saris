from celery import shared_task
from saris_assessment.models import GradeBook
from saris_assessment.services import AppealGradeManager, GradeBookBuilder, ResultManager, SUPGradeManager


@shared_task
def generate_gradebook(gradebook_id):
    try:
        gradebook = GradeBook.get_by_id(gradebook_id)
        if not gradebook.is_pending():
            return
        builder = GradeBookBuilder(gradebook)
        builder.generate()
    except:
        pass


@shared_task
def process_grades(academic_semester):
    try:
        manager = ResultManager(academic_semester)
        manager.process()
    except:
        pass


@shared_task
def publish_grades(academic_semester):
    try:
        manager = ResultManager(academic_semester)
        manager.publish()
    except:
        pass


@shared_task
def process_missing_grades(academic_semester):
    try:
        manager = ResultManager(academic_semester)
        manager.process_missing_grades()
    except:
        pass

@shared_task
def process_appeal_grades(campus):
    try:
        manager = AppealGradeManager(campus)
        manager.check_appeals()
        manager.process()
    except:
        pass


@shared_task
def publish_appeal_grades(campus):
    try:
        manager = AppealGradeManager(campus)
        manager.check_appeals()
        manager.publish()
    except:
        pass



@shared_task
def process_supplementary_grades(campus):
    try:
        manager = SUPGradeManager(campus)
        manager.check_supplementary()
        manager.process()
    except:
        pass


@shared_task
def publish_supplementary_grades(campus):
    try:
        manager = SUPGradeManager(campus)
        manager.check_supplementary()
        manager.publish()
    except:
        pass