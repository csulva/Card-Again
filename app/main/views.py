from re import M
from flask_login.utils import login_required
from app import db
from app.main.forms import EditProfileForm, SearchCardForm, SearchUserForm
from . import main
from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import current_user
from app.models import User, Card, Permission
from datetime import datetime
from ..decorators import permission_required

@main.route('/', methods=["GET", "POST"])
def index():
    form = SearchCardForm()
    if form.validate_on_submit():
        search = form.search.data
        if search == '' or search == ' ':
            flash('Please enter a search...')
            return redirect(url_for('main.no_results', form=form, search=' '))
        elif Card.query.filter(Card.name.ilike(f'%{search}%')).all():
            return redirect(url_for('main.search_results', search=search))
        elif Card.query.filter(Card.set_name.contains(search)).all():
            return redirect(url_for('main.search_results', search=search))
        elif Card.query.filter(Card.name.contains(search)).all() == []:
            return redirect(url_for('main.no_results', search=search))

            # for set in set_names:
            #     if search in set:
            #         new_search = set
            #         cards = Card.query.filter_by(set_name=new_search).all()
            #         return redirect(url_for('main.search_results', search=search))
        else:
            cards = []
            return redirect(url_for('main.no_results', cards=cards, search=search))
    return render_template('index.html', user=current_user, form=form)


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    cards = user.cards.order_by(Card.pokedex_number.asc()).paginate(page, per_page=current_app.config['CARDAGAIN_CARDS_PER_PAGE'],
            error_out=False)

    next_url = url_for('main.user', username=user.username, page=cards.next_num) \
        if cards.has_next else None
    prev_url = url_for('main.user', username=user.username, page=cards.prev_num) \
        if cards.has_prev else None

    total_cards = len(user.cards.all())
    total_normal_market_price = 0
    total_holofoil = 0
    total_reverse = 0
    for card in user.cards:
        if card.normal_price_market:
            total_normal_market_price += card.normal_price_market
        if card.holofoil_price_market:
            total_holofoil += card.holofoil_price_market
        if card.reverse_holofoil_price_market:
            total_reverse += card.reverse_holofoil_price_market

    return render_template('user.html', user=user, cards=cards.items, getattr=getattr, next_url=next_url, prev_url=prev_url, total_normal_market_price=total_normal_market_price, total_holofoil=total_holofoil, total_reverse=total_reverse, total_cards=total_cards)

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
        return redirect(url_for('main.user', username=current_user.username))
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
    return redirect(request.referrer)

@main.route('/remove/<card_id>')
@login_required
@permission_required(Permission.FOLLOW)
def remove(card_id):
    card = Card.query.filter_by(card_id=card_id).first()
    if card is None:
        flash("That is not a valid card.")
        return redirect(url_for('.index'))
    if card not in current_user.cards:
        flash("Looks like you don't have that card in your collection.")
        return redirect(url_for('.card', slug=card.slug))
    current_user.cards.remove(card)
    db.session.commit()
    flash(f"You have successfully removed the card from your collection.")
    return redirect(url_for('.user', username=current_user.username, card_id=card.card_id))

@main.route('/search_results/<search>')
def search_results(search):
    page = request.args.get('page', 1, type=int)
    if Card.query.filter(Card.name.ilike(f'%{search}%')).all():
        length = len(Card.query.filter(Card.name.ilike(f'%{search}%')).all())
        cards = Card.query.filter(Card.name.ilike(f'%{search}%')).order_by(Card.pokedex_number.asc()).paginate(page, per_page=current_app.config['CARDAGAIN_CARDS_PER_PAGE'],
            error_out=False) or Card.query.filter(Card.name.contains(search.title())).order_by(Card.pokedex_number.asc()).paginate(page, per_page=current_app.config['CARDAGAIN_CARDS_PER_PAGE'],
            error_out=False)
    elif Card.query.filter(Card.set_name.contains(search)):
        length = len(Card.query.filter(Card.set_name.contains(search)).all())
        cards = Card.query.filter(Card.set_name.contains(search)).order_by(Card.pokedex_number.asc()).paginate(page, per_page=current_app.config['CARDAGAIN_CARDS_PER_PAGE'],
            error_out=False)
    # elif search:
    #     new_search = []
    #     for set in set_names:
    #         if search in set:
    #             new_search.append(set)
    #     new_cards = []
    #     for new_set in new_search:
    #         cards = Card.query.filter_by(set_name=new_set)
    #         new_cards.append(cards)
    #         length = len(new_cards)
    #     for card in new_cards:
    #         for new_card in card:
    #             cards = Card.query.filter_by(name=new_card.name).order_by(Card.pokedex_number.asc()).paginate(page, per_page=current_app.config['CARDAGAIN_CARDS_PER_PAGE'],
    #             error_out=False)
    next_url = url_for('main.search_results', search=search, page=cards.next_num) \
        if cards.has_next else None
    prev_url = url_for('main.search_results', search=search, page=cards.prev_num) \
        if cards.has_prev else None

    message = f'{length} Results for "{search}"'
    length_per_page = f'{len(cards.items)} Cards Listed on this Page'
    return render_template('search_results.html', message=message, cards=cards.items, search=search, next_url=next_url, prev_url=prev_url, length_per_page=length_per_page)

@main.route('/no_results/<search>', methods=['GET', 'POST'])
def no_results(search):
    form = SearchCardForm()
    if form.validate_on_submit():
        new_search = form.search.data
        if new_search == '' or new_search == ' ':
            flash('Please enter a search...')
            message = f'Your search "{new_search} " yielded no results. Try again.'
            return render_template('no_results.html', form=form, search=new_search, message=message)
        elif Card.query.filter(Card.name.contains(new_search)).all():
            return redirect(url_for('main.search_results', search=new_search))
        elif Card.query.filter(Card.set_name.contains(new_search)).all():
            return redirect(url_for('main.search_results', search=new_search))
        else:
            cards = []
            return redirect(url_for('main.no_results', cards=cards, form=form, search=new_search))
    message = f'Your search "{search}" yielded no results. Try again.'
    return render_template('no_results.html', form=form, message=message)

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page,
        per_page=current_app.config['CARDAGAIN_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # convert to only follower and timestamp
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',
                           user=user,
                           title_text="Followers of",
                           endpoint='.followers',
                           pagination=pagination,
                           follows=follows)

@main.route('/following/<username>')
def following(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.following.paginate(
        page,
        per_page=current_app.config['CARDAGAIN_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # convert to only follower and timestamp
    follows = [{'user': item.following, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('following.html',
                           user=user,
                           title_text="Following",
                           endpoint='.following',
                           pagination=pagination,
                           follows=follows)

# Render search user form
@main.route('/search_users', methods=['GET', 'POST'])
@login_required
def search_users():
    form = SearchUserForm()
    if form.validate_on_submit():
        search = form.search.data
        if search == '' or search == ' ':
            flash('Please enter a valid search...')
            return redirect(url_for('main.no_user_results', search=' '))
        elif User.query.filter_by(username=search).all():
            return redirect(url_for('main.search_user', search=search))
        else:
            search == []
            return redirect(url_for('main.no_user_results', search=search))
    message = 'Search Users'
    return render_template('search_users.html', form=form, message=message)

# Show searched user results
@main.route('/search_user/<search>')
def search_user(search):
    users = User.query.filter_by(username=search).all()
    if users == []:
        return redirect(url_for('main.no_user_results', search=search))
    message = f'{len(users)} Results for "{search}"'
    return render_template('search_user.html', message=message, users=users, search=search)

@main.route('/no_user_results/<search>', methods=['GET', 'POST'])
def no_user_results(search):
    form = SearchUserForm()
    if form.validate_on_submit():
        search = form.search.data
        if search == '':
            flash('Please enter a valid search...')
            return redirect(url_for('main.no_user_results', search=' '))
        elif User.query.filter_by(username=search).all():
            return redirect(url_for('main.search_user', search=search))
        else:
            search == []
            return redirect(url_for('main.no_user_results', search=search))
    message = f'Your search "{search}" yielded no results. Try again.'
    return render_template('no_user_results.html', form=form, message=message)
