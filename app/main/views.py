from . import main
from flask import render_template, url_for

@main.route('/')
def index():
    username = None
    return render_template('index.html', username=username)

@main.route('/test')
def test():
    return render_template('test.html')