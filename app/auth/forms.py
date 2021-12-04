from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Usernames must have only letters, numbers, dots, or underscores')])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords do not match.')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists.')

class ChangeEmail(FlaskForm):
    old_email = StringField("Old Email", validators=[DataRequired(), Email()])
    email = StringField("New Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered by another user.')

class ChangeEmail(FlaskForm):
    old_email = StringField("Old Email", validators=[DataRequired(), Email()])
    email = StringField("New Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered by another user.')

class ChangePassword(FlaskForm):
    password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField('Password', validators=[DataRequired(), EqualTo('new_password_confirm', message='Passwords do not match.'
        )])
    new_password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

class ChangeUsername(FlaskForm):
    new_username = StringField("New Username", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered by another user.')