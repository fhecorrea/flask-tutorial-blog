from flask import (
    Blueprint, flash, redirect, url_for, g, render_template, request
)
from werkzeug.exceptions import abort
from fhblog.auth import login_required
from fhblog.db import get_conn

blueprint = Blueprint('blog', __name__)

@blueprint.route('/')
def index():
    '''
    Defines the main route of app.
    '''
    conn_db = get_conn()
    posts = conn_db.execute(
        'SELECT p.id, p.author_id, p.title, p.body, p.created, u.alias, u.email'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('blog/index.html', posts=posts)

@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['post_title']
        body = request.form['post_text']
        error = None

        if not title:
            error = 'Title is required.'
        elif len(body) < 5:
            error = 'Body must have at least 5 caracters.'

        if error is None:
            conn_db = get_conn()
            conn_db.execute(
                'INSERT INTO post (author_id, title, body)'
                ' VALUES (?, ?, ?)', (g.user['id'], title, body)
            )
            conn_db.commit()
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('blog/create.html')

def get_post(post_id, check_author=True):
    post = get_conn().execute(
        'SELECT p.id, p.author_id, p.title, p.body, p.created, u.alias, u.email'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?', (post_id,)
    ).fetchone()

    if post is None:
        abort(404, 'Post id-{id} doesn\'t exists'.format(id=post_id))

    if check_author and g.user['id'] != post['author_id']:
        abort(403, 'Whoa! You cannot access this!')

    return post

@blueprint.route('/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update(post_id):
    post = get_post(post_id)

    if request.method == 'POST':
        title = request.form['post_title']
        body = request.form['post_text']
        error = None

        if not title:
            error = 'Title is required.'

        if not error:
            conn_db = get_conn()
            conn_db.execute(
                'UPDATE post SET title = ?, body = ? WHERE id = ?',
                (title, body, post_id)
            )
            conn_db.commit()
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('blog/update.html', post=post)

@blueprint.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    get_post(post_id)
    conn_db = get_conn()
    conn_db.execute('DELETE FROM post WHERE id = ?', (post_id, ))
    conn_db.commit()
    return redirect(url_for('blog.index'))
