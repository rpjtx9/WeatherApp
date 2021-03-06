from flask import (
    Flask, flash, redirect, render_template, request, session, url_for, g
    )
import os
import sqlalchemy
from sqlalchemy import text
from weather_data_functions import weather_lookup, WeatherInfo, geocode
from weatherpackage.db import get_db

def create_app(test_config = None):
    # Create the app, configure the secret key and tell Flask that config files are relative to the instance folder.
    # Set database to weather.db which will be created on first run.
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        DATABASE = "sqlite:///"+os.path.join(app.instance_path, "weather.db"),
        DEBUG = True
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
    @app.route("/", methods = ("GET", "POST"))
    def home():
        if request.method == "POST":
            redirect(url_for("home"))
        else:
            user_id = session.get("user_id")
            if user_id is None:
                g.user = None
            else:
                db = get_db()
                g.user = db.execute(text(
                    "SELECT * FROM users WHERE id = :id").bindparams( id = user_id,
                )).fetchone()
            if g.user:
                lat = g.user.home_city_lat
                lng = g.user.home_city_lng
                weather = weather_lookup(lat, lng)
                return render_template("home.html", weather=weather)
            else:
                return render_template("home.html")


    # Register the database with the factory function
    from . import db
    db.init_app(app)


    # Register the authentication  blueprint with the factory function
    from . import auth
    app.register_blueprint(auth.bp)

    # Register the user blueprint with factory
    from . import user
    app.register_blueprint(user.bp)




    return app