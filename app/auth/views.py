from . import auth
from app import db
from flask import render_template, url_for, redirect, flash, request
from .forms import LoginForm, RegistrationForm, ChangeEmail, ChangePassword, ChangeUsername
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.emails import send_email
from werkzeug.urls import url_parse

# Auth view functions

@auth.route('/login', methods=["GET", "POST"])
def login():
    """Function to enable users to login

    Returns:
        auth/login.html file: Loads the login.html page displaying the login form.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    # POST requests - enables users to log in
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password. Try again.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # Redirects to the page the user was on before logging in
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    # GET request - renders the login template url
    return render_template('auth/login.html', title='Log Into Card Again', form=form)

@auth.route('/logout')
def logout():
    """Function to log the user out of the session.

    Returns:
        Redirects to index/home page
    """
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=["GET", "POST"])
def register():
    """Function to let a user register their account to be added to database, login, post.

    Returns:
        auth/register.html file: Renders the registration form and template
    """
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
    """Function to confirm the user's account with their email address.

    Args:
        token (string): Token generated after registering email, or upon request.
        Token is placed in a confirmaiton link that is sent to the user's email address in the database.
    """
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
    """Decorates functions that redirects user to the unconfirmed page
    if the user's account is unconfirmed.

    Returns:
        Redirects to unconfirmed html page if user is unconfirmed.
    """
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request != 'static' \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    """Landing page for users who are signed in but uncofirmed.

    Returns:
        auth/unconfirmed.html file: Renders unconfirmed page.
    """
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)

@auth.route('/resend_confirmation')
def resend_confirmation():
    """Function to resend confirmation link to the user's email
    """
    user = current_user
    token = user.generate_confirmation_token()
    confirmation_link = url_for('auth.confirm', token=token, _external=True)
    send_email(user.email, 'Confirm your account with Ragtime', 'auth/confirm', user=user, confirmation_link=confirmation_link)
    flash('Message sent! Check your email for the new confirmation link.')
    return redirect(url_for('auth.unconfirmed'))

@auth.route('/change-email', methods=["GET", "POST"])
@login_required
def change_email():
    """Function to allow users to change their email address.

    Returns:
        Renders change email form unless POST request--redirects to login page
    """
    form = ChangeEmail()
    # POST request - if form is submitted to change email
    if form.validate_on_submit():
        old_email = form.old_email.data
        email = form.email.data
        # Old email entered must match users' current email
        if current_user.email == old_email:
            current_user.email = email
            db.session.add(current_user)
            db.session.commit()
            flash('You have successfully changed your email address.')
            return redirect(url_for('auth.login'))
        else:
            flash('Your old email does not match our records. Please try again.')
    # GET request - returns the template url with the form
    return render_template('auth/change-email.html', form=form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Function to allow users to change their password

    Returns:
        Renders change password form, unless POST request--redirects to login page
    """
    form = ChangePassword()
    # POST request - if form is submitted, changes the user's password
    if form.validate_on_submit():
        password = form.password.data
        new_password = form.new_password.data
        # Old password must match current password
        if current_user.check_password(password) == True:
            current_user.set_password(new_password)
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been changed successfully.')
            return redirect(url_for('auth.login'))
        else:
            flash('Old password does not match records. Try again.')
    # GET request - returns change password template url with change password form
    return render_template('auth/change-password.html', form=form)

@auth.route('/change-username', methods=["GET", "POST"])
@login_required
def change_username():
    """Function to allow users to change their username

    Returns:
        Renders change username form, unless POST request--redirects to login page
    """
    form = ChangeUsername()
    # POST request - if user submits change password form
    if form.validate_on_submit():
        username = form.new_username.data
        current_user.username = username
        db.session.add(current_user)
        db.session.commit()
        flash('You have successfully changed your username.')
        return redirect(url_for('auth.login'))
    # GET request - returns change username template url with change username form
    return render_template('auth/change-username.html', form=form)
