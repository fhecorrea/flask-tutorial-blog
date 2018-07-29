from os import makedirs, path
from flask import Flask

def create_app(test_config=None):

    # Creating a new instance of appl
    app = Flask(__name__, instance_relative_config=True)
    # Set the settings
    app.config.from_mapping(
        SECRET_KEY='development',
        DATABASE=path.join(app.instance_path, 'flask.sqlite')
    )

    # verify if the instance test config. does exist
    if test_config is None:
        # if not, it sets up from a Python file
        app.config.from_pyfile('config.py', silent=True)
    else:
        #if so, get that instance
        app.config.from_mapping(test_config)

    try:
        #it ensure that database path exists
        makedirs(app.instance_path)
    except OSError:
        pass

    from . import db, auth, blog
    db.init_app(app)
    app.register_blueprint(auth.blueprint)
    app.register_blueprint(blog.blueprint)
    app.add_url_rule('/', endpoint='index')

    return app
