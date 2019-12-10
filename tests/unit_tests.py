import os
import tempfile

import pytest
from flask_bcrypt import Bcrypt

import app
from models import User


@pytest.fixture
def client():
    app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True
    app.app.config['WTF_CSRF_ENABLED'] = False
    app_client = app.app.test_client()
    app_context = app.app.app_context()
    app_context.push()
    yield app_client
    app_context.pop()


@pytest.fixture()
def init_db():
    app.db.create_all()
    yield app.db
    app.db.drop_all()


@pytest.fixture()
def init_bcrypt():
    yield app.bcrypt


def test_empty_db(client):
    rv = client.get('/')
    assert b'App Sec' in rv.data


def test_register_form(client):
    rv = client.get('/register')
    assert b'id="pword"' in rv.data


def test_login_form(client):
    rv = client.get('/login')
    assert b'id="pword"' in rv.data


def test_login_failure(client, init_db):
    rv = client.post('/login', data=dict(
        username="greg",
        password="greg_p",
        phonenumber="333"
    ))
    assert b"Incorrect" in rv.data


def test_login_success(client, init_db,init_bcrypt):
    bcrypt_hash = init_bcrypt.generate_password_hash("greg_p")
    user = User(name="greg", phone_number="333", password_hash=bcrypt_hash)
    init_db.session.add(user)
    init_db.session.commit()
    rv = client.post('/login', data=dict(
        username="greg",
        password="greg_p",
        phonenumber="333"
    ))
    assert b"Success" in rv.data


def test_registration_success(client, init_db):
    client.post('/register', data=dict(
        username="greg1",
        password="greg_p1",
        phonenumber="333"
    ))
    user = User.query.filter_by(name="greg1").first()
    assert user.name == "greg1"


def test_spell_check_auth(client):
    rv = client.get('/spell_check')
    assert rv.status_code == 401


def test_spell_check_get(client, init_db, init_bcrypt):
    bcrypt_hash = init_bcrypt.generate_password_hash("greg_p")
    user = User(name="greg", phone_number="333", password_hash=bcrypt_hash)
    init_db.session.add(user)
    init_db.session.commit()
    rv = client.post('/login', data=dict(
        username="greg",
        password="greg_p",
        phonenumber="333"
    ))
    assert b"Success" in rv.data
    rv2 = client.get('/spell_check')
    assert b'id="inputtext"' in rv2.data


def test_spell_check_success(client, init_db, init_bcrypt):
    bcrypt_hash = init_bcrypt.generate_password_hash("greg_p")
    user = User(name="greg", phone_number="333", password_hash=bcrypt_hash)
    init_db.session.add(user)
    init_db.session.commit()
    rv = client.post('/login', data=dict(
        username="greg",
        password="greg_p",
        phonenumber="333"
    ))
    assert b"Success" in rv.data
    rv2 = client.post('/spell_check', data=dict(
        text="hello bye bds"
    ))
    assert b'hello bye bds' in rv2.data


def test_spell_check_sql_inject(client, init_db,init_bcrypt):
    bcrypt_hash = init_bcrypt.generate_password_hash("greg_p")
    user = User(name="greg", phone_number="333", password_hash=bcrypt_hash)
    init_db.session.add(user)
    init_db.session.commit()
    rv = client.post('/login', data=dict(
        username="greg",
        password="greg_p",
        phonenumber="333"
    ))
    assert b"Success" in rv.data
    rv2 = client.post('/spell_check', data=dict(
        text="hello; drop table user; --"
    ))
    user = User.query.get(1)
    assert user is not None


def test_logs(client, init_db, init_bcrypt):
    admin_user = User(name="admin", phone_number="12345678901",
                      password_hash=b'$2b$12$0HVKc/rDTJOYXRaGdFBPeu.ZdEH0F3uMvUV/AEmoKLXDHUp7pQb8O')
    init_db.session.add(admin_user)
    init_db.session.commit()
    bcrypt_hash1 = init_bcrypt.generate_password_hash("greg_p")
    user2 = User(name="greg", phone_number="333", password_hash=bcrypt_hash1)
    init_db.session.add(user2)
    init_db.session.commit()
    rv2 = client.post('/login', data=dict(
        username="greg",
        password="greg_p",
        phonenumber="333"
    ))
    assert b"Success" in rv2.data
    rv = client.post('/login', data=dict(
        username="admin",
        password="Administrator@1",
        phonenumber="12345678901"
    ))
    assert b"Success" in rv.data
    rv4 = client.get('/admin/history/log/2')
    print(rv4.data)
    assert b"time" in rv4.data


def test_query_history(client, init_db, init_bcrypt):
    bcrypt_hash = init_bcrypt.generate_password_hash("greg_p")
    user = User(name="greg", phone_number="333", password_hash=bcrypt_hash)
    init_db.session.add(user)
    init_db.session.commit()
    rv = client.post('/login', data=dict(
        username="greg",
        password="greg_p",
        phonenumber="333"
    ))
    assert b"Success" in rv.data
    rv2 = client.post('/spell_check', data=dict(
        text="hello bye bds"
    ))
    assert b'hello bye bds' in rv2.data
    rv4 = client.get('/history/query1')
    assert b"querytext" in rv4.data