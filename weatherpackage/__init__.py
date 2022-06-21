from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy

def create_app(test_config = None):
    # Create the app, configure the secret key and tell Flask that config files are relative to the instance folder.
    # Set database to weather.db which will be created on first run.
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = "dev",
        SQLALCHEMY_DATABASE_URI = "sqlite:///"+os.path.join(app.instance_path, "weather.db"),
        SQLALCHEMY_ECHO = True,
        # Track modifications set to false as it is unneeded and flask throws a warning every time you start it up otherwise. If you want to use the event system for Flask-SQLAlchemy then this will need to be True.
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    # Check for test configurations
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Homepage
    @app.route("/")
    def index():
        return render_template("index.html")

    
    # Register the database with the factory function
    from . import db
    db.init_app(app)

    # Register the authentication  blueprint w ith the factory function
    from . import auth
    app.register_blueprint(auth.bp)

    return app