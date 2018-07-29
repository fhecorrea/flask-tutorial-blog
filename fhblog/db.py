import sqlite3
import click

from flask import current_app, g
from flask.cli import with_appcontext

def get_conn():
    '''
        'g' is a special object that store data.
        It is one for each request
    '''
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_conn(e=None):
    conndb = g.pop('db', None)

    if conndb is not None:
        conndb.close()

def init_database():
    conndb = get_conn()
    with current_app.open_resource('schema.sql') as func:
        conndb.executescript(func.read().decode('utf8'))

@click.command('initdb')
@with_appcontext
def initdb_command():
    click.echo('Initializing the database...')
    init_database()
    click.echo('... database was initialized.')

def init_app(app):
    app.teardown_appcontext(close_conn)
    app.cli.add_command(initdb_command)
