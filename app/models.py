from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import json


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

    # change this
    def __repr__(self):
        return f'<Card_ID: {self.card_id}>'

    @staticmethod
    def insert_cards():
        with open('API/card_ids.json', 'r') as fin:
            ids = json.load(fin)
        for card_id in ids:
            card = Card(card_id=card_id)
            db.session.add(card)
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