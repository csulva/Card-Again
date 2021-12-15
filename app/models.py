from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import json
import re


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    about_me = db.Column(db.String(140))
    name = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)

    cards = db.relationship('Card', backref='owner', lazy='dynamic')

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self) -> str:
        return '<User {}>'.format(self.username)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size=128):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/monsterid/{digest}?d=identicon&s={size}'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            if self.username == current_app.config['CARDAGAIN_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        # if self.email is not None and self.avatar_hash is None:
        #     self.avatar_hash = self.email_hash()
        # self.follow(self)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    @staticmethod
    def make_new_users_user_role():
        for u in User.query.all():
            if u.role == None:
                u.role = Role.query.filter_by(default=True).first()
                db.session.commit()

    def generate_confirmation_token(self, expiration_sec=3600):
        s = Serializer(current_app.secret_key, expiration_sec)
        return s.dumps({'confirm_id': self.id}).decode('utf-8')

    def confirm(self, token):
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
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    # get followers' collections
    def followed_card_collections(self):
        followed = Card.query.join(
            followers, (followers.c.followed_id == Card.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Card.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Card.id.asc())

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String())
    rarity = db.Column(db.String())
    pokedex_number = db.Column(db.Integer)
    image = db.Column(db.String())
    url = db.Column(db.String())
    last_updated = db.Column(db.String())
    normal_price_low = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    normal_price_mid = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    normal_price_high = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    normal_price_market = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    holofoil_price_low = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    holofoil_price_mid = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    holofoil_price_high = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    holofoil_price_market = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    reverse_holofoil_price_low = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    reverse_holofoil_price_mid = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    reverse_holofoil_price_high = db.Column(db.Float(precision=(10, 2), asdecimal=True))
    reverse_holofoil_price_market = db.Column(db.Float(precision=(10, 2), asdecimal=True))

    slug = db.Column(db.String(128), unique=True)

    def __repr__(self):
        return f'<Card_ID: {self.card_id}>'

    @staticmethod
    def generate_slug():
        for card in Card.query.all():
            card.slug = f"{card.id}-" + re.sub(r'[^\w]+', '-', card.card_id.lower())
            db.session.add(card)
        db.session.commit()

    @staticmethod
    def insert_cards():
        with open('API/card_data.json', 'r') as fin:
            data = json.load(fin)
        for info in data:
            card_id=info['id']
            name=info['name']
            rarity=info['rarity']
            pokedex_number=info['pokedex_number']
            image=info['image']
            url=info['url']
            last_updated=info['last_updated']
            try:
                if info['price']['normal']['low']:
                    normal_price_low = float(info['price']['normal']['low'])
            except:
                normal_price_low=None
            try:
                if info['price']['normal']['mid']:
                    normal_price_mid = float(info['price']['normal']['mid'])
            except:
                normal_price_mid=None
            try:
                if info['price']['normal']['high']:
                    normal_price_high = float(info['price']['normal']['high'])
            except:
                normal_price_high=None
            try:
                if info['price']['normal']['market']:
                    normal_price_market = float(info['price']['normal']['market'])
            except:
                normal_price_market=None
            try:
                if info['price']['holofoil']['low']:
                    holofoil_price_low = float(info['price']['holofoil']['low'])
            except:
                holofoil_price_low=None
            try:
                if info['price']['holofoil']['mid']:
                    holofoil_price_mid = float(info['price']['holofoil']['mid'])
            except:
                holofoil_price_mid=None
            try:
                if info['price']['holofoil']['high']:
                    holofoil_price_high = float(info['price']['holofoil']['high'])
            except:
                holofoil_price_high=None
            try:
                if info['price']['holofoil']['market']:
                    holofoil_price_market = float(info['price']['holofoil']['market'])
            except:
                holofoil_price_market=None
            try:
                if info['price']['reverseHolofoil']['low']:
                    reverse_holofoil_price_low = float(info['price']['reverseHolofoil']['low'])
            except:
                reverse_holofoil_price_low=None
            try:
                if info['price']['reverseHolofoil']['mid']:
                    reverse_holofoil_price_mid = float(info['price']['reverseHolofoil']['mid'])
            except:
                reverse_holofoil_price_mid=None
            try:
                if info['price']['reverseHolofoil']['high']:
                    reverse_holofoil_price_high = float(info['price']['reverseHolofoil']['high'])
            except:
                reverse_holofoil_price_high=None
            try:
                if info['price']['reverseHolofoil']['market']:
                    reverse_holofoil_price_market = float(info['price']['reverseHolofoil']['market'])
            except:
                reverse_holofoil_price_market=None

            card=Card(card_id=card_id, name=name, rarity=rarity, pokedex_number=pokedex_number,
            image=image, url=url, last_updated=last_updated,
            normal_price_low=normal_price_low, normal_price_mid=normal_price_mid, normal_price_high=normal_price_high, normal_price_market=normal_price_market,
            holofoil_price_low=holofoil_price_low, holofoil_price_mid=holofoil_price_mid, holofoil_price_high=holofoil_price_high, holofoil_price_market=holofoil_price_market,
            reverse_holofoil_price_low=reverse_holofoil_price_low, reverse_holofoil_price_mid=reverse_holofoil_price_mid, reverse_holofoil_price_high=reverse_holofoil_price_high, reverse_holofoil_price_market=reverse_holofoil_price_market)
            db.session.add(card)
        Card.generate_slug()
        db.session.commit()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Permission:
    FOLLOW = 1
    REVIEW = 2
    PUBLISH = 4
    MODERATE = 8
    ADMIN = 16

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f'<Role: {self.name}>'

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
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