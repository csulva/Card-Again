from . import auth
from app import db
from flask import render_template, url_for, redirect, flash, request
from .forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.email import send_email
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
            token = user.generate_confirmation_token()
            confirmation_link = url_for('auth.confirm', token=token, _external=True)
            send_email(user.email, 'Welcome to Card Again!', 'mail/welcome', user=user)
            send_email(user.email, 'Confirm your account with Card Again', 'auth/confirm',  confirmation_link=confirmation_link)
            send_email('chrservices15@gmail.com', 'A new user has been created!', 'mail/new_user', user=user)
            flash('Thanks for registering! Check your email for a link to confirm your account.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form, title='Register for Card Again')

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash("You're already confirmed!")
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account! Thank you.')
    else:
        flash("Whoops! That confirmation link either expired, or it isn't valid.")
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request != 'static' \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)

@auth.route('/resend_confirmation')
def resend_confirmation():
    user = current_user
    token = user.generate_confirmation_token()
    confirmation_link = url_for('auth.confirm', token=token, _external=True)
    send_email(user.email, 'Confirm your account with Ragtime', 'auth/confirm', user=user, confirmation_link=confirmation_link)
    flash('Message sent! Check your email for the new confirmation link.')
    return redirect(url_for('auth.unconfirmed'))