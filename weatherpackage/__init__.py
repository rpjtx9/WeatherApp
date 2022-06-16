from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy

def create_app(test_config = None):
    # Create the app, configure the secret key and tell Flask that config files are relative to the instance folder.
    # Set database to weather.db which will be created later
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = "dev",
        DATABASE = os.path.join(app.instance_path, "weather.db")
    )

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
    return app