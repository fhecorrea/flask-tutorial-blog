import functools

from time import time
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from fhblog.db import get_conn

blueprint = Blueprint('auth', __name__, url_prefix='/auth')

@blueprint.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_conn().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        alias = request.form['alias']
        email = request.form['email']
        passwd = request.form['passwd']
        conn_db = get_conn()
        error = None

        if not email:
            error = 'E-mail is required!'
        elif not passwd:
            error = 'Password is required!'
        elif conn_db.execute(
                'SELECT * FROM user WHERE email = ?', (email,)
            ).fetchone() is not None:
            error = 'An User with e-mail' + email + 'already exists!'

        if alias is None or alias == '':
            alias = email[0:email.find('@')]


        if error is None:
            # TODO: use this -> http://flask-bcrypt.readthedocs.io/en/latest/
            conn_db.execute(
                'INSERT INTO user (alias, email, passwd) VALUES (?, ?, ?)',
                (alias, email, generate_password_hash(passwd))
            )
            conn_db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        passwd = request.form['passwd']
        conn_db = get_conn()
        error = None
        user = conn_db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['passwd'], passwd):
            error = 'Incorrect username'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['logged_in'] = time()
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
