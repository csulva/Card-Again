from flask import current_app
from API.load import load_cards
from app.models import Card
from app import scheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import logging

# logging.basicConfig()
logger = logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# Schedule tasks at given time -- day_of_week=0 is Monday
@scheduler.task('cron', id='update_cards_task', day_of_week=0, hour=17, minute=0)
def update_cards_task():
    """Function to run other functions as a task, with scheduer.task
    """
    with scheduler.app.app_context():
        load_cards()
        Card.insert_cards()
        Card.update_cards()

# Run if EVENT_JOB_ERROR occurs (from above scheduler task)
def error_callback(error):
    with scheduler.app.app_context():
        current_app.logger.error('Error with task occurred.')
        print('logging messages')
        current_app.logger.debug(f'Error object was {error}.')

scheduler.add_listener(error_callback, EVENT_JOB_ERROR)
# scheduler.add_listener(error_callback, EVENT_JOB_EXECUTED)

