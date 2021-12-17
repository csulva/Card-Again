from flask_login.utils import login_required
from app import db
from app.main.forms import EditProfileForm
from . import main
from flask import render_template, url_for, flash, redirect, request
from flask_login import current_user
from app.models import User, Card, Permission
from datetime import datetime
from ..decorators import permission_required

@main.route('/')
def index():
    return render_template('index.html', user=current_user)

@main.route('/test')
@login_required
def test():
    return render_template('test.html')

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user, cards=user.cards, getattr=getattr)

@main.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@main.route('/edit-profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash("Looks like you are already following that user.")
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"You are now following {username}")
    return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash("Looks like you aren't already following that user.")
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You have successfully unfollowed {username}.")
    return redirect(url_for('.user', username=username))

@main.route('/card/<slug>')
def card(slug):
    card = Card.query.filter_by(slug=slug).first_or_404()
    slug = card.slug
    return render_template('card.html', cards=[card], slug=slug, getattr=getattr)

@main.route('/add/<card_id>')
@login_required
@permission_required(Permission.FOLLOW)
def add(card_id):
    card = Card.query.filter_by(card_id=card_id).first()
    if card is None:
        flash("That is not a valid card.")
        return redirect(url_for('.index'))
    if card in current_user.cards:
        flash("Looks like you are already have that card in your collection.")
        return redirect(url_for('.card', slug=card.slug))
    current_user.cards.append(card)
    db.session.commit()
    flash(f"You have added the card to your collection.")
    return redirect(url_for('.user', username=current_user.username, card_id=card.card_id))