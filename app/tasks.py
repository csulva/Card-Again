from API.load import load_cards
from app.models import Card
from app import scheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


@scheduler.task('interval', id='update_cards', day_of_week=(0,4), hour=0)
def update_cards():
    with scheduler.app.app_context():
        load_cards()
        Card.insert_cards()
        Card.update_cards()

scheduler.add_listener(update_cards, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
