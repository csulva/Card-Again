from pymysql import IntegrityError
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login.mixins import AnonymousUserMixin
from hashlib import md5
from datetime import datetime
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import json
import re
import logging


# Relationship table "follows" -- one-to-many -- connects User to Users through follower and following
class Follow(db.Model):
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Relationship table "collections" -- many-to-many -- joins Users to Cards
collections = db.Table('collections',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('card_id', db.Integer, db.ForeignKey('card.id'))
    )

# Database table "users"
class User(UserMixin, db.Model):
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Required for registration
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    confirmed = db.Column(db.Boolean, default=False)

    # Foreign key to "roles" table
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # Editable in profile
    about_me = db.Column(db.String(140))
    name = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to "cards" table
    cards = db.relationship('Card', secondary=collections, backref='owner', lazy='dynamic')

    # Who the user is following
    following = db.relationship('Follow',
                foreign_keys=[Follow.follower_id],
                backref=db.backref('follower', lazy='joined'),
                lazy='dynamic',
                cascade='all, delete-orphan')
    # Who the user has as followers
    followers = db.relationship('Follow',
                foreign_keys=[Follow.following_id],
                backref=db.backref('following', lazy='joined'),
                lazy='dynamic',
                cascade='all, delete-orphan')

    def __repr__(self) -> str:
        """Returns 'User' + username
        """
        return '<User {}>'.format(self.username)

    def __init__(self, **kwargs):
        """Creates user role automatically upon registration of new user. Users set to follow themselves
        upon registration as well.
        """
        super().__init__(**kwargs)
        if self.role is None:
            if self.username == current_app.config['CARDAGAIN_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        self.follow(self)

    @property
    def password(self):
        """
        Raises:
            AttributeError: if password is requested from the database. Ensures passwords cannot
            easily be accessed from the user's information.
        """
        raise AttributeError('Password is not a readable attribute')

    def set_password(self, password):
        """Securely creates a password hash with the user's password to be saved in the database,
        instead of the password.

        Args:
            password (string): the user's actual password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Returns True is password in database matches the one entered in the function call,
        False if not.

        Args:
            password (string): the password to be input to check/verify if correct
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size=128):
        """Creates an avatar/profile photo for the user based on their email address.
        Photos are created with Gravatar API.

        Args:
            size (int, optional): size of the avatar photo in pixels. Defaults to 128.

        Returns:
            string: url of the user's profile image
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/monsterid/{digest}?d=identicon&s={size}'

    def can(self, perm):
        """Returns True if user can perform a permission (perm) provided, False if not.

        Args:
            perm (int): permission defined by an integer in the Permissions table
        """
        return self.role is not None and self.role.has_permission(perm)

    def ping(self):
        """When the user is active, their last_seen column updates to now.
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def is_administrator(self):
        """Returns True if the user has the Administrator role, False if not.
        """
        return self.can(Permission.ADMIN)

    @staticmethod
    def make_new_users_user_role():
        """If users have no current roles, this function ensures they are created as a User role.
        """
        for u in User.query.all():
            if u.role == None:
                u.role = Role.query.filter_by(default=True).first()
                db.session.commit()

    def generate_confirmation_token(self, expiration_sec=3600):
        """Generates confirmation token so that when a new user registers on the site,
        an email will be sent with the token, to confirm the user.

        Args:
            expiration_sec (int, optional): Token expires in 60 minutes. Defaults to 3600 seconds.

        Returns:
            string: Unique token string
        """
        s = Serializer(current_app.secret_key, expiration_sec)
        return s.dumps({'confirm_id': self.id}).decode('utf-8')

    def confirm(self, token):
        """Confirms user in the database, user table. Returns True if user is confirmed
        based on the token generated for their account.

        Args:
            token (string): Unique token string to confirm account.
        """
        s = Serializer(current_app.secret_key)
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm_id') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def follow(self, user):
        """Lets user follow another user.

        Args:
            user (class): A user in the database
        """
        if not self.is_following(user):
            f = Follow(follower=self, following=user)
            db.session.add(f)

    def unfollow(self, user):
        """Lets user unfollow another user

        Args:
            user (class): A user in the database
        """
        f = self.following.filter_by(following_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        """Checks if current user is following the user provided in calling the function

        Args:
            user (class): A user in the database
        """
        if user.id is None:
            return False
        return self.following.filter_by(following_id=user.id).first() is not None

    @staticmethod
    def add_self_follows():
        """All users follow themselves.
        """
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

# Database table "card"
class Card(db.Model):
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Imported from the API - Pokémon TCG Developers API
    card_id = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(200))
    rarity = db.Column(db.String(200))
    pokedex_number = db.Column(db.Integer)
    image = db.Column(db.String(200))
    set_name = db.Column(db.String(200))
    set_series = db.Column(db.String(200))
    url = db.Column(db.String(200))
    last_updated = db.Column(db.String(200))
    normal_price_low = db.Column(db.Float(asdecimal=True))
    normal_price_mid = db.Column(db.Float(asdecimal=True))
    normal_price_high = db.Column(db.Float(asdecimal=True))
    normal_price_market = db.Column(db.Float(asdecimal=True))
    holofoil_price_low = db.Column(db.Float(asdecimal=True))
    holofoil_price_mid = db.Column(db.Float(asdecimal=True))
    holofoil_price_high = db.Column(db.Float(asdecimal=True))
    holofoil_price_market = db.Column(db.Float(asdecimal=True))
    reverse_holofoil_price_low = db.Column(db.Float(asdecimal=True))
    reverse_holofoil_price_mid = db.Column(db.Float(asdecimal=True))
    reverse_holofoil_price_high = db.Column(db.Float(asdecimal=True))
    reverse_holofoil_price_market = db.Column(db.Float(asdecimal=True))

    slug = db.Column(db.String(128), unique=True)

    def __repr__(self):
        return f'<Card_ID: {self.card_id}>'

    @staticmethod
    def generate_slug():
        """Creates random string slug associated with the card, used in URL of the card
        """
        for card in Card.query.all():
            card.slug = f"{card.id}-" + re.sub(r'[^\w]+', '-', card.card_id.lower())
            db.session.add(card)
        db.session.commit()

    @staticmethod
    def insert_cards():
        """Adds all card data to the database when function is called. Data is taken from
        card_data.json file, which loads the data from the API.
        """
        # Load data in json format
        with open('API/card_data.json', 'r') as fin:
            data = json.load(fin)
        for dicts in data:
            card = dicts['id']
            if not Card.query.filter_by(card_id=card).first():
                card_id=dicts['id']
                name=dicts['name']
                rarity=dicts['rarity']
                pokedex_number=dicts['pokedex_number']
                image=dicts['image']
                set_name=dicts['set_name']
                set_series=dicts['set_series']
                url=dicts['url']
                last_updated=dicts['last_updated']
                try:
                    if dicts['price']['normal']['low']:
                        normal_price_low = float(dicts['price']['normal']['low'])
                except:
                    normal_price_low=None
                try:
                    if dicts['price']['normal']['mid']:
                        normal_price_mid = float(dicts['price']['normal']['mid'])
                except:
                    normal_price_mid=None
                try:
                    if dicts['price']['normal']['high']:
                        normal_price_high = float(dicts['price']['normal']['high'])
                except:
                    normal_price_high=None
                try:
                    if dicts['price']['normal']['market']:
                        normal_price_market = float(dicts['price']['normal']['market'])
                except:
                    normal_price_market=None
                try:
                    if dicts['price']['holofoil']['low']:
                        holofoil_price_low = float(dicts['price']['holofoil']['low'])
                except:
                    holofoil_price_low=None
                try:
                    if dicts['price']['holofoil']['mid']:
                        holofoil_price_mid = float(dicts['price']['holofoil']['mid'])
                except:
                    holofoil_price_mid=None
                try:
                    if dicts['price']['holofoil']['high']:
                        holofoil_price_high = float(dicts['price']['holofoil']['high'])
                except:
                    holofoil_price_high=None
                try:
                    if dicts['price']['holofoil']['market']:
                        holofoil_price_market = float(dicts['price']['holofoil']['market'])
                except:
                    holofoil_price_market=None
                try:
                    if dicts['price']['reverseHolofoil']['low']:
                        reverse_holofoil_price_low = float(dicts['price']['reverseHolofoil']['low'])
                except:
                    reverse_holofoil_price_low=None
                try:
                    if dicts['price']['reverseHolofoil']['mid']:
                        reverse_holofoil_price_mid = float(dicts['price']['reverseHolofoil']['mid'])
                except:
                    reverse_holofoil_price_mid=None
                try:
                    if dicts['price']['reverseHolofoil']['high']:
                        reverse_holofoil_price_high = float(dicts['price']['reverseHolofoil']['high'])
                except:
                    reverse_holofoil_price_high=None
                try:
                    if dicts['price']['reverseHolofoil']['market']:
                        reverse_holofoil_price_market = float(dicts['price']['reverseHolofoil']['market'])
                except:
                    reverse_holofoil_price_market=None
                    # Adds data to their respective columns for each card
                card=Card(card_id=card_id, name=name, rarity=rarity, pokedex_number=pokedex_number,
                image=image, set_name=set_name, set_series=set_series, url=url, last_updated=last_updated,
                normal_price_low=normal_price_low, normal_price_mid=normal_price_mid, normal_price_high=normal_price_high, normal_price_market=normal_price_market,
                holofoil_price_low=holofoil_price_low, holofoil_price_mid=holofoil_price_mid, holofoil_price_high=holofoil_price_high, holofoil_price_market=holofoil_price_market,
                reverse_holofoil_price_low=reverse_holofoil_price_low, reverse_holofoil_price_mid=reverse_holofoil_price_mid, reverse_holofoil_price_high=reverse_holofoil_price_high, reverse_holofoil_price_market=reverse_holofoil_price_market)
                db.session.add(card)
            else:
                pass

        Card.generate_slug()
        db.session.commit()
        current_app.logger.debug('Everything working.')

    @staticmethod
    def update_cards():
        """Updates all card data of each card. Data is taken from
        card_data.json file, which loads the data from the API.
        """
        # Load data in json format
        with open('API/card_data.json', 'r') as fin:
            data = json.load(fin)
        for dicts in data:
            id = dicts['id']
            card = Card.query.filter_by(card_id=id).first()
            card.card_id=dicts['id']
            card.name=dicts['name']
            card.rarity=dicts['rarity']
            card.pokedex_number=dicts['pokedex_number']
            card.image=dicts['image']
            card.set_name=dicts['set_name']
            card.set_series=dicts['set_series']
            card.url=dicts['url']
            card.last_updated=dicts['last_updated']
            try:
                if dicts['price']['normal']['low']:
                    card.normal_price_low = float(dicts['price']['normal']['low'])
            except:
                card.normal_price_low=None
            try:
                if dicts['price']['normal']['mid']:
                    card.normal_price_mid = float(dicts['price']['normal']['mid'])
            except:
                card.normal_price_mid=None
            try:
                if dicts['price']['normal']['high']:
                    card.normal_price_high = float(dicts['price']['normal']['high'])
            except:
                card.normal_price_high=None
            try:
                if dicts['price']['normal']['market']:
                    card.normal_price_market = float(dicts['price']['normal']['market'])
            except:
                card.normal_price_market=None
            try:
                if dicts['price']['holofoil']['low']:
                    card.holofoil_price_low = float(dicts['price']['holofoil']['low'])
            except:
                card.holofoil_price_low=None
            try:
                if dicts['price']['holofoil']['mid']:
                    card.holofoil_price_mid = float(dicts['price']['holofoil']['mid'])
            except:
                card.holofoil_price_mid=None
            try:
                if dicts['price']['holofoil']['high']:
                    card.holofoil_price_high = float(dicts['price']['holofoil']['high'])
            except:
                card.holofoil_price_high=None
            try:
                if dicts['price']['holofoil']['market']:
                    card.holofoil_price_market = float(dicts['price']['holofoil']['market'])
            except:
                card.holofoil_price_market=None
            try:
                if dicts['price']['reverseHolofoil']['low']:
                    card.reverse_holofoil_price_low = float(dicts['price']['reverseHolofoil']['low'])
            except:
                card.reverse_holofoil_price_low=None
            try:
                if dicts['price']['reverseHolofoil']['mid']:
                    card.reverse_holofoil_price_mid = float(dicts['price']['reverseHolofoil']['mid'])
            except:
                card.reverse_holofoil_price_mid=None
            try:
                if dicts['price']['reverseHolofoil']['high']:
                    card.reverse_holofoil_price_high = float(dicts['price']['reverseHolofoil']['high'])
            except:
                card.reverse_holofoil_price_high=None
            try:
                if dicts['price']['reverseHolofoil']['market']:
                    card.reverse_holofoil_price_market = float(dicts['price']['reverseHolofoil']['market'])
            except:
                card.reverse_holofoil_price_market=None

            # Add changes
            db.session.add(card)
        Card.generate_slug()
        # Commit changes
        db.session.commit()
        current_app.logger.debug('Cards updated.')

# Loads user based on id
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Quantifying Role Permissions
class Permission:
    FOLLOW = 1
    REVIEW = 2
    PUBLISH = 4
    MODERATE = 8
    ADMIN = 16

# Database table "roles"
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic') # This relationship enables users to access roles
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __init__(self, **kwargs):
        """Role set to permission 0 unless otherwise specified
        (such as in the insert_roles() static method below)
        """
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f'<Role: {self.name}>'

    def add_permission(self, perm):
        """Adds specified permission to a provided user

        Args:
            perm (int): The integer related to specific permissions (see above Permissions class)
        """
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        """Removes a given permission from the provided user. User must already have that role
        """
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        """Resets user permission to 0, or no permissions
        """
        self.permissions = 0

    def has_permission(self, perm):
        """Returns True or False if user has given perm, or not

        Args:
            perm (int): The integer related to specific permissions (see above Permissions class)
        """
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        """Creates roles below and adds them to the database, roles table
        """
        roles = {
            'User':             [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH],
            'Moderator':        [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH,
                                 Permission.MODERATE],
            'Administrator':    [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH,
                                 Permission.MODERATE,
                                 Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            # see if role is already in table
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # it's not so make a new one
                role = Role(name=r)
            role.reset_permissions()
        # add whichever permissions the role needs
            for perm in roles[r]:
                role.add_permission(perm)
            # if role is the default one, default is True
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

# Anonymous user class
class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        """Anonymous user has no permissions, so it returns False

        Args:
            perm (int): permission defined by an integer in the Permissions table
        """
        return False

    def is_administrator(self):
        """Anonymous user is not an administrator, so it returns False
        """
        return False

# Manages anonymous user class
login_manager.anonymous_user = AnonymousUser
