from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SearchField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import User

# Edit profile form, asks user's name, and about_me
class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=0, max=64)])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

# Search for card form
class SearchCardForm(FlaskForm):
    search = SearchField('Search for a card by "Pokémon" name or "Set" name...')
    submit = SubmitField('Submit')

# Search for user form
class SearchUserForm(FlaskForm):
    search = SearchField('Search for a User by their username...')
    submit = SubmitField('Submit')