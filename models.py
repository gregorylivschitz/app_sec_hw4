from flask_login import UserMixin


from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    phone_number = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    spell_check = db.relationship("SpellCheck", backref="user")
    log_logs = db.relationship("LogLogs", backref="user")


class SpellCheck(db.Model):
    __tablename__ = 'spell_check'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    submit_text = db.Column(db.String())
    result_text = db.Column(db.String())


class LogLogs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    login_time = db.Column(db.DateTime())
    logout_time = db.Column(db.DateTime())

