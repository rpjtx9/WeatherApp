from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import os
import sqlite3

def create_app(test_config = None):
    # Create the app, configure the secret key and tell Flask that config files are relative to the instance folder
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = "dev"
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Session will use filesystem
    app.config["SESSION_TYPE"] = "filesystem"



    # Homepage
    @app.route("/")
    def index():
        return render_template("index.html")
