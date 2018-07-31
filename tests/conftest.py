from os import path, close, unlink
from tempfile import mkstemp
import pytest

from fhblog import create_app
from fhblog.db import get_conn, init_database

with open(path.join(path.dirname(__file__), 'data.sql'), 'rb') as fl:
    HDL_SQL = fl.read().decode('utf8')

@pytest.fixture
def app():
    db_file_dir, db_path = mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    with app.app_context():
        init_database()
        get_conn().executescript(HDL_SQL)

    yield app

    close(db_file_dir)
    unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions():
    def __init__(self, client):
        self._client = client

    def login(self, email='silva@mail.com', passwd='test'):
        return self._client.post(
            '/auth/login',
            data={'email': email, 'passwd': passwd}
        )
    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)
