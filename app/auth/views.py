from . import auth
from flask import render_template, url_for
from .forms import LoginForm

@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    # validation
    # flash

    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=["GET", "POST"])
def register():


    return render_template('auth/register.html')
