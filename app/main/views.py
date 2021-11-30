from flask_login.utils import login_required
from app import db
from app.auth.views import login
from . import main
from flask import render_template, url_for
from flask_login import current_user
from app.models import User, Card
from datetime import datetime

@main.route('/')
def index():
    return render_template('index.html', user=current_user)

@main.route('/test')
@login_required
def test():
    return render_template('test.html')

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    cards = []
    return render_template('user.html', user=user, cards=cards)

@main.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()