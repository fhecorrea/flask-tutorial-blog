import pytest
from fhblog.db import get_conn

def test_index(client, auth):
    response = client.get('/')
    html_as_text = response.get_data(as_text=True)
    assert "Log in" in html_as_text
    assert "Register" in html_as_text

    auth.login()
    assert "My first post" in html_as_text
    assert "Hello everybody.\nToo long, you didn&#39;t read." in html_as_text
    assert "by Silva on 18 Jun 2018" in html_as_text

    # The variable 'refreshed_page' is to force a update on the page. 
    # Without it, the client continues with the old page loaded in the tests beginning
    refreshed_page = client.get('/')
    refreshed_html_as_text = refreshed_page.get_data(as_text=True)
    assert "href=\"/auth/logout\"" in refreshed_html_as_text
    assert "href=\"/1/update\"" in refreshed_html_as_text
    assert "href=\"/1/\"" in refreshed_html_as_text

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
    assert client.get('/create').status_code == 201
    client.post('/create', data={'post_title': 'another one', 'post_text': 'hello everybody!'})

    with app.app_context():
        conn_db = get_conn()
        count = conn_db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 5

def test_reading(client, auth):
    # Accessing as an unlogged user
    response = client.get('/3/')
    assert response.status_code == 200
    html_page_as_text = response.get_data(as_text=True)
    assert "Many troubles..." in html_page_as_text
    assert "In this post, we are going to talk about something." in html_page_as_text
    #assert "by Silva on 06 Jul 2018" in html_page_as_text
    assert "href=\"/3/update\"" not in html_page_as_text
    # Logging in and acessing the same resource
    auth.login()
    new_response = client.get('/3/')
    assert b"href=\"/3/update\"" in new_response.data

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
