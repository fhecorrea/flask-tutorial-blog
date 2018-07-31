from flask import g, session
import pytest
from fhblog.db import get_conn

def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register',
        data={'alias':'Outro', 'email':'outro@mail.com', 'passwd':'12345'}
    )
    assert response.headers['Location'] == 'http://localhost/auth/login'

    with app.app_context():
        assert get_conn().execute(
            "SELECT * FROM user WHERE email = 'outro@mail.com'"
        ).fetchone() is not None

@pytest.mark.parametrize(
    ('alias', 'email', 'passwd', 'message'), (
        ('', '', '123', b'E-mail is required'),
        ('User alias', 'email@serve.comr', '', b'Password is required'),
        ('Silva', 'silva@mail.com', '123456', b'already exists')
    )
)
def test_register_validate_input(client, alias, email, passwd, message):
    response = client.post(
        '/auth/register',
        data={'alias' : alias, 'email': email, 'passwd': passwd}
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['email'] == 'silva@mail.com'

@pytest.mark.parametrize(
    ('email', 'passwd', 'message'), (
        ('asdasd', '4a4', b'Incorrect user or password.'),
        ('august@mail.com', '1234', b'Incorrect user or password.')
    )
)
def test_login_validate_input(auth, email, passwd, message):
    response = auth.login(email, passwd)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
