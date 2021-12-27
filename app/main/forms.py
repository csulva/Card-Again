from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SearchField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import User


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=0, max=64)])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class SearchCardForm(FlaskForm):
    search = SearchField('Search for cards...')
    submit = SubmitField('Submit')

class SearchUserForm(FlaskForm):
    search = SearchField('Search for a User...')
    submit = SubmitField('Submit')