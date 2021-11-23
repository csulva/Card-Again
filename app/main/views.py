from re import L
from app import app
from flask import render_template, url_for

@app.route('/')
def index():
    username = None
    return render_template('index.html', username=username)

@app.route('/login')
def login():
    return render_template('login.html')