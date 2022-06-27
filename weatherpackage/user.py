import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, g
)
from werkzeug.security import check_password_hash, generate_password_hash
from weatherpackage.db import get_db
from sqlalchemy import text, exc
from weather_data_functions import weather_lookup, WeatherInfo, LocationInfo, geocode

bp = Blueprint("user", __name__, url_prefix = "/user")

# Before_app_request makes this load no matter what. That way the user is available to all pages
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    
    db = get_db()
    g.user = db.execute(text(
        "SELECT * FROM users WHERE id = :id").bindparams( id = user_id,
    )).fetchone()


# Profile view
@bp.route("/profile", methods = ("GET", "POST"))
def profile():
    # Only have one POST option for now, choosing a home city
    if request.method == "POST":
        # Grab the zip code from the request
        zipcode = request.form["city_zip"]
        # Get the latitude and longitude from the zip code
        location = geocode(zipcode)
        # Store all 3 into the user's profile
        db = get_db()
        user_id = session.get("user_id")
        try:
            db.execute(text("UPDATE users SET home_city_lat = :lat, home_city_lng = :lng, home_city_zip = :zip, home_city_name = :name WHERE id = :id").bindparams(lat = location.results[0].geometry.location.lat, lng = location.results[0].geometry.location.lng, zip = zipcode, name = location.results[0].address_components[1].long_name, id = user_id))
        except IndexError:
            flash("Please enter a valid zipcode")
            return redirect(url_for("user.profile"))
        flash("Home city set!", "success")
        return redirect(url_for("user.profile"))
    else:
        return render_template('user/profile.html')
