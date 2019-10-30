import os
import tempfile

import pytest

import app


@pytest.fixture
def client():
    db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True

    with app.app.test_client() as client:
        with app.app.app_context():
            app.db.create_all()
        yield client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE'])


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


# def test_login_success(client):
#     rv = client.post('/register', data=dict(
#         uname="greg",
#         pword="mypassword",
#         fa="564-3843-2093"
#     ))
#     assert b'id="success"' in rv.data