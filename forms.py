from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, TextAreaField


class SpellCheckForm(FlaskForm):
    text = TextAreaField("Input text here", id="inputtext", validators=[validators.DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', id="uname", validators=[validators.Length(min=4, max=25), validators.DataRequired()])
    phonenumber = StringField('Phone Number', id="2fa", validators=[validators.DataRequired()])
    password = PasswordField('New Password', id="pword", validators= [validators.DataRequired()])


class RegistrationForm(FlaskForm):
    username = StringField('Username', id="uname",validators=[validators.Length(min=4, max=25), validators.DataRequired()])
    phonenumber = StringField('Phone Number', id="2fa", validators=[validators.DataRequired()])
    # password = PasswordField('New Password', id="pword",validators= [
    #     validators.DataRequired(),
    #     validators.EqualTo('confirm', message='Passwords must match')
    # ])
    password = PasswordField('New Password', id="pword", validators=[validators.DataRequired()])
    # confirm = PasswordField('Repeat Password')