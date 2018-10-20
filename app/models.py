from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from . import login_manager
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), index = True)
    email = db.Column(db.String(255),unique = True, index = True)
    bio = db.Column(db.String(1000))
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    profile_pic_path = db.Column(db.String)
    password_secure = db.Column(db.String(255))
    pitches = db.relationship('Pitch',backref = 'user', lazy = 'dynamic')
    comments = db.relationship('Comment',backref = 'user', lazy = 'dynamic')
    is_admin = db.Column(db.Boolean,default = False)

    @property
    def password(self):
        raise AttributeError('You cannot read the password attribute')

    @password.setter
    def password(self,password):
        self.password_secure = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_secure,password)

    def __repr__(self):
        return f'User{self.username},{self.email}'


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(255))
    users = db.relationship('User',backref = 'role',lazy="dynamic")

    def __repr__(self):
        return f'User {self.name}'


class Pitch(db.Model):
    __tablename__ = 'pitches'
    id = db.Column(db.Integer,primary_key = True)
    pitch_title = db.Column(db.String)
    pitch_content = db.Column(db.String(1000))
    category = db.Column(db.String(), nullable = False)
    posted = db.Column(db.DateTime,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    comments = db.relationship('Comment',backref =  'pitch_id',lazy = "dynamic")


    def save_pitch(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_pitches(cls,category):
        pitches = Pitch.query.filter_by(category = category).all()
        return pitches

    @classmethod
    def get_pitch(cls,id):
        pitch = Pitch.query.filter_by(id = id).first()

        return pitch

    @classmethod
    def count_pitches(cls,uname):
        user = User.query.filter_by(username = uname).first()
        pitches = Pitch.query.filter_by(user_id = user.id).all()

        pitch_count = 0
        for pitch in pitches:
            pitch_count += 1

        return pitch_count

    def __repr__(self):
        return f'Pitch {self.pitch_title}, {self.category}'


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key = True)
    comment = db.Column(db.String(1000))
    name = db.Column(db.String)
    pitch = db.Column(db.Integer,db.ForeignKey("pitches.id"))
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))

    def save_comment(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_comments(cls,pitch):
        comments = Comment.query.filter_by(pitch_id = pitch).all()
        return comments

    def __repr__(self):
        return f'Comment{self.comment}'


class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(20))
    email = db.Column(db.String(), unique = True)
