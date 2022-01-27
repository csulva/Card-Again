from API.load import load_cards
from app.models import Card
from app import scheduler
# from flask import current_app
# app=current_app._get_current_object()
# with app.app_context():

@scheduler.task('interval', id='update_cards', seconds=30)
def update_cards():
    # load_cards()
    print('test cards loaded')
    Card.insert_cards()
    print('new cards inserted into db')
    Card.update_cards()
    print('cards updated')