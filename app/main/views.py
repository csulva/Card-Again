from . import main
from flask import render_template, url_for

@main.route('/')
def index():
    username = None
    return render_template('index.html', username=username)

@main.route('/login')
def login():
    return render_template('login.html')