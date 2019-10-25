from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    phone_number = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    # active = db.Column(db.Boolean())
