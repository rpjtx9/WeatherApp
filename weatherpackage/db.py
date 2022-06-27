from encodings import utf_8
from sqlalchemy import (
    Table,  Column, Integer, String, MetaData, ForeignKey, create_engine, FLOAT, DATE, UniqueConstraint, select, insert)
import click
from flask import current_app, g
from flask.cli import with_appcontext
import os
import csv
from datetime import datetime

# from sqlalchemy import String, Integer

# Need to decide which one of these two database connection functions to use, if any! Might just use sqlitealchemy?
# Function 1

def get_db():
    """Get the SQLAlchemy database object"""
    if 'db' not in g:
        g.engine = create_engine("sqlite:///"+os.path.join(current_app.instance_path, "weather.db"))
        g.db = g.engine.connect()
    return g.db

def init_db():
    """Command that will be executed via CLI due to click"""
    engine = create_engine("sqlite:///"+os.path.join(current_app.instance_path, "weather.db"))
    meta = MetaData()
    # Wipe existing database if it already exists
    engine.execute("DROP TABLE IF EXISTS users;")
    engine.execute("DROP TABLE IF EXISTS cities;")
    # Create users table. Home city is foreign key to geonameid in cities table
    users = Table(
        "users", meta,
        Column("id", Integer, primary_key = True),
        Column("username", String, unique = True, nullable = False),
        Column("password_hashed", String, nullable = False),
        Column("home_cityid", Integer, ForeignKey("cities.id")),
        Column("email_add", String, unique= True)
    )
    # Create cities table
    cities = Table(
        "cities", meta,
        Column("id", Integer, primary_key = True),
        Column("geonameid", Integer),
        Column("name", String, nullable = False),
        Column("asciiname", String),
        Column("alternatenames", String),
        Column("latitude", FLOAT),
        Column("longitude", FLOAT),
        Column("country_code", String),
        Column("admin1", String),
        Column("admin2", String),
        Column("admin3", String),
        Column("admin4", String),
        Column("elevation", FLOAT),
        Column("timezone", String),
        Column("mod_date", DATE)
    )
    meta.create_all(engine)
    # Create connection to database for insertion of city data and store a list of column names for city table. Also create the buffer list to do a bulk insert.
    db = engine.connect()
    buffer = []

    # Store the path information for where city data is located
    static_path = os.path.join(current_app.root_path, "static\cities")
    cityfilepaths = [os.path.join(static_path, name) for name in os.listdir(static_path)]
    # Loop for each file containing city data. Files must be stored in the static path of the application package.
    for cityfile in cityfilepaths:
        # Open each text file and read it
        with open(cityfile, encoding= "utf8") as file:
            reader = csv.reader(file, dialect=csv.excel_tab)
            # Each line on the reader will have a total of 18 items 0 indexed. We will not be using items 6, 7, 9, 14, or 16
            for line in reader:
                # Change empty strings to None
                empty_to_null = lambda i : i or None
                nulled_line = [empty_to_null(i) for i in line]
                # Add to buffer list
                buffer.append({               
                    "geonameid": int(nulled_line[0]),
                    "name" : nulled_line[1],
                    "asciiname" : nulled_line[2],
                    "alternatenames" : nulled_line[3],
                    "latitude" : nulled_line[4],
                    "longitude" : nulled_line[5],
                    "country_code" : nulled_line[8],
                    "admin1" : nulled_line[10],
                    "admin2" : nulled_line[11],
                    "admin3" : nulled_line[12],
                    "admin4" : nulled_line[13],
                    "elevation" : nulled_line[15],
                    "timezone" : nulled_line[17],
                    "mod_date" : datetime.strptime(nulled_line[18],"%Y-%m-%d")
                })
                if len(buffer) >= 100:
                    # Bulk insert the city data            
                    db.execute(cities.insert().values(buffer))
                    buffer = []

    # Insert the last < 100 rows of buffer
    db.execute(cities.insert().values(buffer))

                


def close_db(e=None):
    """Closes database on teardown"""
    db = g.pop('db', None)
    if db is not None:
        db.close()



@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear  existing data and create new tables"""
    init_db()
    click.echo("Initialized the database")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)