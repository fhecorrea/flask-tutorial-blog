from sqlite3 import ProgrammingError
from pytest import raises
from fhblog.db import get_conn

def test_open_and_close_db(app):
    with app.app_context():
        conn_db = get_conn()
        assert conn_db is get_conn()

    with raises(ProgrammingError) as prog_err:
        conn_db.execute('SELECT * FROM user')

    assert 'closed' in str(prog_err)

def test_init_database_command(runner, monkeypatch):
    class Recorder():
        called = False

    def fake_init_database():
        Recorder.called = True

    monkeypatch.setattr('fhblog.db.init_database', fake_init_database)
    result = runner.invoke(args=['initdb'])
    assert 'database was initialized' in result.output
    assert Recorder.called
