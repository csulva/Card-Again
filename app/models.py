from app import db




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    cards = db.relationship('Card', backref='owner', lazy='dynamic')

    def __repr__(self) -> str:
        return '<User {}>'.format(self.username)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # change this
    # def __repr__(self):
    #     return '<Post {}>'.format(self.body)