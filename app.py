import datetime
import subprocess

import flask
import sqlalchemy
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, request, flash, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm, SpellCheckForm, QueryForm, LoggerForm
from flask_talisman import Talisman

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

from models import User, SpellCheck, LogLogs

app.config['SECRET_KEY'] = 'FAKE KEY FOR CI/CD'
db.create_all()
bcrypt = Bcrypt(app)
# unfortunately this doesn't work when running unit tests with python app.py, need to run it as flask run
# so I'm commenting out so travis would work
# Talisman(app)
login_manager = LoginManager()
login_manager.init_app(app)
# add admin user
admin_user = User(name="admin", phone_number="12345678901", password_hash=b'$2b$12$0HVKc/rDTJOYXRaGdFBPeu.ZdEH0F3uMvUV/AEmoKLXDHUp7pQb8O')
db.session.add(admin_user)
db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def hello_world():
    return render_template("index.html")


#https://flask.palletsprojects.com/en/1.0.x/patterns/wtforms/
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        password = form.password.data
        bcrypt_hash = bcrypt.generate_password_hash(password=password)
        try:
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
            log_log = LogLogs(user_id=user.id, login_time=datetime.datetime.now())
            db.session.add(log_log)
            db.session.commit()
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
    last_log = current_user.log_logs[-1]
    logout_user()
    last_log.logout_time = datetime.datetime.now()
    db.session.commit()
    return redirect("/")


@app.route('/spell_check', methods=['GET', 'POST'])
@login_required
def get_spell_check():
    form = SpellCheckForm(request.form)
    if request.method == 'POST' and form.validate():
        full_text = form.text.data
        with open("test_3.txt", 'w') as f:
            f.write(full_text)
        # result = subprocess.run(['./spell_check', 'test_3.txt', 'wordlist.txt'], stdout=subprocess.PIPE)
        # result = "boo hoo"
        # words = result.stdout.decode("utf-8").splitlines()
        words = ["omg", "omg2"]
        misspelled = ','.join(words)
        user_id = current_user.id
        sp = SpellCheck(user_id=user_id, submit_text=full_text, result_text=misspelled)
        db.session.add(sp)
        db.session.commit()
        return render_template("spell_check_return.html", misspelled=misspelled, full_text=full_text)
    return render_template('spell_check.html', form=form)


# @app.route('/your/webroot/history', methods=['GET', 'POST'])
@app.route('/history', methods=['GET', 'POST'])
@login_required
def get_history():
    # usernames are unique so we don't have to worry here
    if current_user.name == 'admin':
        form = QueryForm(request.form)
        if request.method == 'POST' and form.validate():
            query_id = form.data['query_id']
            # could this be an issue?
            return redirect('/history/query{}'.format(query_id))
        return render_template("query_admin.html", form=form)
    return render_template("query_history.html", query_spells=current_user.spell_check)


# @app.route('/your/webroot/history/<int:query_id>')
@app.route('/history/query<int:query_id>', methods=['GET', 'POST'])
@login_required
def get_query(query_id):
    if current_user.name == 'admin':
        sp = SpellCheck.query.get(query_id)
        return render_template("query_info.html", sp=sp)
    for spell_check in current_user.spell_check:
        if spell_check.id == query_id:
            sp = SpellCheck.query.get(query_id)
            return render_template("query_info.html", sp=sp)
    return "No query info found"


# @app.route('/your/webroot/login_history', methods=['GET', 'POST'])
@app.route('/login_history', methods=['GET', 'POST'])
@login_required
def get_login_history():
    if current_user.name == 'admin':
        form = LoggerForm(request.form)
        if request.method == 'POST' and form.validate():
            user_id = form.data['user_id']
            # could this be an issue?
            return redirect('/admin/history/log/{}'.format(user_id))
        return render_template("log_admin.html", form=form)
    return "DENIED", 401


@app.route('/admin/history/log/<int:user_id>')
@login_required
def get_logging(user_id):
    if current_user.name == 'admin':
        log_logs = User.query.get(user_id).log_logs
        return render_template("log_history.html", log_logs=log_logs)
    return "DENIED", 401


if __name__ == '__main__':
    app.run(debug=True)
