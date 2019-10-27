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
    """Start with a blank database."""
    rv = client.get('/')
    assert b'App Sec' in rv.data