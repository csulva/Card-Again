from flask_login.utils import login_required
from app.auth.views import login
from . import main
from flask import render_template, url_for

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/test')
@login_required
def test():
    return render_template('test.html')