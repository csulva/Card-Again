from . import auth
from app import db
from flask import render_template, url_for, redirect, flash, request
from .forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse

@auth.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password. Try again.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Log Into Card Again', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        email_entered = form.email.data
        username_entered = form.username.data
        password_entered = form.password.data
        user = User.query.filter_by(username=username_entered).first()
        if user is None:
            user = User(username=username_entered, email=email_entered)
            user.set_password(password_entered)
            db.session.add(user)
            db.session.commit()
            # token = user.generate_confirmation_token()
            # confirmation_link = url_for('auth.confirm', token=token, _external=True)
            # send_email(user.email, 'Welcome to Ragtime!', 'mail/welcome', user=user)
            # send_email(user.email, 'Confirm your account with Ragtime', 'auth/confirm',  confirmation_link=confirmation_link)
            # send_email('chrservices15@gmail.com', 'A new user has been created!', 'mail/new_user', user=user)
            flash('Thanks for registering!')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form, title='Register for Card Again')