from celery import shared_task
from saris_graduation.models import Booklet
from saris_graduation.services import BookletBuilder, CandidatesManager


@shared_task
def generate_booklet(booklet_id):
    booklet = Booklet.get_by_id(booklet_id)
    if not booklet.is_pending():
        return
    builder = BookletBuilder(booklet)
    builder.generate()
    

@shared_task
def process_candidates(session, campus):
    try:
        manager = CandidatesManager(session, campus)
        manager.process()
    except:
        pass


