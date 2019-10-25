import flask
import sqlalchemy
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, request, flash, render_template
from flask_login import LoginManager, login_user, login_required, logout_user
from forms import RegistrationForm, LoginForm, SpellCheckForm
import subprocess
# db.init_app(app)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
db = SQLAlchemy(app)

from models import User


app.config['SECRET_KEY'] = 'FAKE KEY FOR CI/CD'
db.create_all()
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def hello_world():
    return 'Hello World!'


#https://flask.palletsprojects.com/en/1.0.x/patterns/wtforms/
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        print("in post registration")
        password = form.password.data
        # confirm_password = form.confirm.data
        # if password != confirm_password:
        #     return '<div id="success">failure</div>'
        bcrypt_hash = bcrypt.generate_password_hash(password=password)
        try:
            print("trying to add user {}".format(form.username.data))
            user = User(name=form.username.data, phone_number=form.phonenumber.data, password_hash=bcrypt_hash)
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return '<div id="success">failure</div>'
        print("succeeded render success back")
        return '<div id="success">success</div>'
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        if validate_user(username, password):
            user = User.query.filter_by(name=username).first()
            if user.phone_number != form.phonenumber.data:
                return '<div id="result">Two-factor failure</div>'
            login_user(user)
            # next = flask.request.args.get('next')
            # # is_safe_url should check if the url is safe for redirects.
            # # See http://flask.pocoo.org/snippets/62/ for an example.
            # if not is_safe_url(next):
            #     return flask.abort(400)
            return '<div id="result">Success</div>'
        return '<div id="result">Incorrect</div>'
    return render_template('login.html', form=form)


def validate_user(username, password):
    found_user = User.query.filter_by(name=username).first()
    if found_user:
        return bcrypt.check_password_hash(found_user.password_hash, password)
    return False


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/spell_check', methods=['GET', 'POST'])
@login_required
def get_spell_check():
    form = SpellCheckForm(request.form)
    if request.method == 'POST' and form.validate():
        full_text = form.text.data
        with open("test_3.txt", 'w') as f:
            f.write(full_text)
        result = subprocess.run(['./spell_check', 'test_3.txt', 'wordlist.txt'], stdout=subprocess.PIPE)
        words = result.stdout.splitlines()
        misspelled = b','.join(words)
        return render_template("spell_check_return.html", misspelled=misspelled, full_text=full_text)
    return render_template('spell_check.html', form=form)


if __name__ == '__main__':
    app.run()
