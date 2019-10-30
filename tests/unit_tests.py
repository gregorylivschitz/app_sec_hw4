import os
import tempfile

import pytest
from flask_bcrypt import Bcrypt

import app
from models import User


@pytest.fixture
def client():
    db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
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
    print(rv)
    assert b'id="pword"' in rv.data


def test_login_failure(client, init_db):
    rv = client.post('/login', data=dict(
        username="greg",
        password="greg_p",
        phonenumber="333"
    ))
    assert b"Incorrect" in rv.data


# def test_login_success(client, init_bcrypt):
#     bcrypt_hash = init_bcrypt("greg")
#     user = User(username="greg", password_hash=bcrypt_hash, phone_number="333")
#     init_db.session.add(user)
#     init_db.session.commit()
#     rv = client.post('/login', data=dict(
#         username="greg",
#         password="greg_p",
#         phonenumber="333"
#     ))
#     assert b"Incorrect" in rv.data