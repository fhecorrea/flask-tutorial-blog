import pytest
from fhblog.db import get_conn

def test_index(client, auth):
    response = client.get('/')
    assert b"Log in" in response.data
    assert b"Register" in response.data

    auth.login()
    # TODO: Fix that issue with login->refresh->appearing of "Log out"
    #assert b"Log out" in response.data
    assert b"My first post" in response.data
    #assert b"Too long, you didn't read." in response.data
    #assert b"by Silva on 18-jun-2018" in response.data
    #assert b"href=\"/1/update\"" in response.data

@pytest.mark.parametrize(
    'path', (
        '/create',
        '/2/update',
        '/2/delete',
    )
)
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_author_required(app, client, auth):
    with app.app_context():
        conn_db = get_conn()
        conn_db.execute('UPDATE post SET author_id = 2 WHERE id = 2')
        conn_db.commit()

    auth.login()
    assert client.post('/2/update').status_code == 403
    assert client.post('/2/delete').status_code == 403
    assert b'href="/2/update"' not in client.get('/').data

@pytest.mark.parametrize(
    'path', (
        '/5/update',
        '/5/delete',
    )
)
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'post_title': 'another one', 'post_text': 'hello everybody!'})

    with app.app_context():
        conn_db = get_conn()
        count = conn_db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 5

def test_update(client, auth, app):
    auth.login()
    assert client.get('/3/update').status_code == 200
    client.post('/3/update', data={'post_title': 'updated', 'post_text': 'a different body'})

    with app.app_context():
        conn_db = get_conn()
        post = conn_db.execute('SELECT * FROM post WHERE id = 3').fetchone()
        assert post['title'] == 'updated'
        assert post['body'] == 'a different body'

@pytest.mark.parametrize(
    'path', (
        '/create',
        '/1/update',
    )
)
def test_create_update_validate(app, client, auth, path):
    auth.login()
    response = client.post(path, data={'post_title': '', 'post_text': ''})

    ##########
    with app.app_context():
        row = get_conn().execute('SELECT * FROM post WHERE id = 1').fetchone()
        print(row[3])
    # assert response.status_code == 400
    assert b'Title is required.' in response.data

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        conn_db = get_conn()
        post = conn_db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None
