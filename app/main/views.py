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
    """Index or home page.

    Returns:
        html file: Returns index.html from the templates directory
    """
    form = SearchCardForm()
    # POST request -- if form is submitted
    if form.validate_on_submit():
        search = form.search.data
        # Where to redirect
        if search == '' or search == ' ':
            flash('Please enter a search...')
            return redirect(url_for('main.no_results', form=form, search=' '))
        elif Card.query.filter(Card.name.ilike(f'%{search}%')).all():
            return redirect(url_for('main.search_results', search=search))
        elif Card.query.filter(Card.set_name.ilike(f'%{search}%')).all():
            return redirect(url_for('main.search_results', search=search))
        elif Card.query.filter(Card.name.ilike(f'%{search}%')).all() == []:
            return redirect(url_for('main.no_results', search=search))
        else:
            cards = []
            return redirect(url_for('main.no_results', cards=cards, search=search))
    # GET - Return homepage template
    return render_template('index.html', user=current_user, form=form)

@main.route('/user/<username>')
@login_required
def user(username):
    """The profile page of the given user is shown

    Args:
        username (string): The user's username is provided in the function to view the user's profile

    Returns:
        user.html file: Shows the page that is the user's profile
    """
    # Find the user based on the username provided, or return 404 error
    user = User.query.filter_by(username=username).first_or_404()
    # Paginate the user's card collection
    page = request.args.get('page', 1, type=int)
    cards = user.cards.order_by(Card.pokedex_number.asc()).paginate(page, per_page=current_app.config['CARDAGAIN_CARDS_PER_PAGE'],
            error_out=False)

    next_url = url_for('main.user', username=user.username, page=cards.next_num) \
        if cards.has_next else None
    prev_url = url_for('main.user', username=user.username, page=cards.prev_num) \
        if cards.has_prev else None

    # Calculating numbers in the user's collection
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
    """Generally, for an authenticated user, their last_seen information will update automatically
    as they use the app
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@main.route('/edit-profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    """The edit profile function renders the page where the user can edit their profile--only
    their own profile

    Returns:
        edit_profile.html file: The page where one can edit their profile
    """
    form = EditProfileForm()
    # POST request - if the user submits the form
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.user', username=current_user.username))
    # GET request shows the page and the user's current information (name, about_me)
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    """This function allows the current user to follow another user

    Args:
        username (string): The given username of the user you would like to follow

    Returns:
        user.html: Redirects back to the user's profile of the user you follow
    """
    # Search database for that user by their username
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash("Looks like you are already following that user.")
        return redirect(url_for('.user', username=username))
    # Call the follow function and commit to database
    current_user.follow(user)
    db.session.commit()
    flash(f"You are now following {username}")
    return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    """This function allows the user to unfollow another user

    Args:
        username (string): The given username of the user you would like to unfollow

    Returns:
        user.html: Redirects back to the user's profile of the user you unfollow
    """
    # Search for the user based on the username
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash("Looks like you aren't already following that user.")
        return redirect(url_for('.user', username=username))
    # Calls the unfollow function and commits it to database
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You have successfully unfollowed {username}.")
    return redirect(url_for('.user', username=username))

@main.route('/card/<slug>')
def card(slug):
    """Function to be able to view the card

    Args:
        slug (string): Each card has a unique slug, and it's used to yield that particular
        card

    Returns:
        card.html file: Shows the particular card on its page
    """
    # Search the database for the card by its slug provided, or return 404 error
    card = Card.query.filter_by(slug=slug).first_or_404()
    slug = card.slug
    return render_template('card.html', cards=[card], slug=slug, getattr=getattr)

@main.route('/add/<card_id>')
@login_required
@permission_required(Permission.FOLLOW)
def add(card_id):
    """This function allows the user to add a card to their collection based
    on the card id

    Args:
        card_id (string): id of the card as provided from the API to the database (not the primary key id)

    Returns:
        The user remains on the current page even when the function is ran and the card added
    """
    # Search for the correct card based on the card id
    card = Card.query.filter_by(card_id=card_id).first()
    if card is None:
        flash("That is not a valid card.")
        return redirect(url_for('.index'))
    if card in current_user.cards:
        flash("Looks like you are already have that card in your collection.")
        return redirect(url_for('.card', slug=card.slug))
    # Adds card to the users collection of "cards" and commits it to database
    current_user.cards.append(card)
    db.session.commit()
    flash(f"You have added the card to your collection.")
    return redirect(request.referrer)

@main.route('/remove/<card_id>')
@login_required
@permission_required(Permission.FOLLOW)
def remove(card_id):
    """This function allows the user to remove a card from their collection based
    on the card id

    Args:
        card_id (string): id of the card as provided from the API to the database (not the primary key id)

    Returns:
        Redirects to the profile of the current user
    """
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
    """Returns cards rendered in html based on the search provided

    Args:
        search (string): The user's input/search that redirects to this page
    """
    page = request.args.get('page', 1, type=int)
    # Searches for cards based on if the search "is like" the name of the card
    if Card.query.filter(Card.name.ilike(f'%{search}%')).all():
        # Number of cards listed
        length = len(Card.query.filter(Card.name.ilike(f'%{search}%')).all())
        # Cards yielded from the search based on the name
        cards = Card.query.filter(Card.name.ilike(f'%{search}%')).order_by(Card.pokedex_number.asc()).paginate(page, per_page=current_app.config['CARDAGAIN_CARDS_PER_PAGE'],
            error_out=False)
    # Searches for cards based on if the search "is like" the set_name of the card
    elif Card.query.filter(Card.set_name.ilike(f'%{search}%')):
        # Number of cards listed
        length = len(Card.query.filter(Card.set_name.ilike(f'%{search}%')).all())
        # Cards yielded from the search based on the set_name
        cards = Card.query.filter(Card.set_name.ilike(f'%{search}%')).order_by(Card.pokedex_number.asc()).paginate(page, per_page=current_app.config['CARDAGAIN_CARDS_PER_PAGE'],
            error_out=False)

    next_url = url_for('main.search_results', search=search, page=cards.next_num) \
        if cards.has_next else None
    prev_url = url_for('main.search_results', search=search, page=cards.prev_num) \
        if cards.has_prev else None

    message = f'{length} Results for "{search}"'
    length_per_page = f'{len(cards.items)} Cards Listed on this Page'
    return render_template('search_results.html', message=message, cards=cards.items, search=search, next_url=next_url, prev_url=prev_url, length_per_page=length_per_page)

@main.route('/no_results/<search>', methods=['GET', 'POST'])
def no_results(search):
    """Returns the "no results" page if the search yields no results based on the
    search form and functions. The no results page also has another search form to allow
    users to search again.

    Args:
        search (string): The user's input/search that redirects to this page -- because no
        cards/results were yielded
    """
    # Renders the search form again
    form = SearchCardForm()
    # POST request - if the form is submitted
    if form.validate_on_submit():
        new_search = form.search.data
        # Redirects to the appropriate pages based on the search
        if new_search == '' or new_search == ' ':
            flash('Please enter a search...')
            message = f'Your search "{new_search} " yielded no results. Try again.'
            return render_template('no_results.html', search=new_search, message=message, form=form)
        elif Card.query.filter(Card.name.ilike(f'%{new_search}%')).all():
            return redirect(url_for('main.search_results', search=new_search))
        elif Card.query.filter(Card.set_name.ilike(f'%{new_search}%')).all():
            return redirect(url_for('main.search_results', search=new_search))
        else:
            cards = []
            return redirect(url_for('main.no_results', cards=cards, form=form, search=new_search))
    # GET request - shows the message in the no_results.html template
    message = f'Your search "{search}" yielded no results. Try again.'
    return render_template('no_results.html', form=form, message=message)

@main.route('/followers/<username>')
def followers(username):
    """Function returns all the followers of the user provided by the username

    Args:
        username (string): The given username of the user who has the followers

    Returns:
        followers.html file: Renders a page displaying followers of the user based on the
        username given in the function
    """
    # Search the database for the user based on the username provided
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    # Paginate the list of followers
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page,
        per_page=current_app.config['CARDAGAIN_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # convert to only follower and timestamp
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title_text="Followers of", endpoint='.followers', pagination=pagination, follows=follows)

@main.route('/following/<username>')
def following(username):
    """Function returns all users who are followed by the user provided by the username

    Args:
        username (string): The given username of the user is following others

    Returns:
        following.html file: Renders a page displaying users who the given user is following
    """
    # Search for user in the database based on the username provided
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    # Paginate the list of users who the current user is following
    page = request.args.get('page', 1, type=int)
    pagination = user.following.paginate(
        page,
        per_page=current_app.config['CARDAGAIN_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # convert to only follower and timestamp
    follows = [{'user': item.following, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('following.html', user=user, title_text="Following", endpoint='.following', pagination=pagination, follows=follows)

@main.route('/search_users', methods=['GET', 'POST'])
@login_required
def search_users():
    """Returns the template to be able to search for other users with the Search User Form
    """
    form = SearchUserForm()
    # POST request - if the form is submitted
    if form.validate_on_submit():
        search = form.search.data
        # Redirects based on the search
        if search == '' or search == ' ':
            flash('Please enter a valid search...')
            return redirect(url_for('main.no_user_results', search=' '))
        elif User.query.filter_by(username=search).all():
            return redirect(url_for('main.search_user', search=search))
        else:
            search == []
            return redirect(url_for('main.no_user_results', search=search))
    # GET request - returns the message in the template
    message = 'Search Users'
    return render_template('search_users.html', form=form, message=message)

@main.route('/search_user/<search>')
def search_user(search):
    """Users are returned and rendered on the page if they match the search from the
    "search_users" view function

    Args:
        search (string): The user's input/search that redirects to this page
    """
    # Search for the user based on if the search matches a username
    users = User.query.filter_by(username=search).all()
    # If no users, returns to the no user results page. Needed?
    if users == []:
        return redirect(url_for('main.no_user_results', search=search))
    # Returns the message as well as the user -- if any -- and renders on the page
    message = f'{len(users)} Results for "{search}"'
    return render_template('search_user.html', message=message, users=users, search=search)

@main.route('/no_user_results/<search>', methods=['GET', 'POST'])
def no_user_results(search):
    """Returns the no_user_results page if no results were yielded when the user
    tried to search for other users.

    Args:
        search (string): The user's input/search that redirects to this page -- because no
        users were yielded
    """
    form = SearchUserForm()
    # POST request - if form is submitted to search for users
    if form.validate_on_submit():
        search = form.search.data
        # Redirects
        if search == '':
            flash('Please enter a valid search...')
            return redirect(url_for('main.no_user_results', search=' '))
        elif User.query.filter_by(username=search).all():
            return redirect(url_for('main.search_user', search=search))
        else:
            search == []
            return redirect(url_for('main.no_user_results', search=search))
    # GET request - renders the no_user_results template with the message
    message = f'Your search "{search}" yielded no results. Try again.'
    return render_template('no_user_results.html', form=form, message=message)
