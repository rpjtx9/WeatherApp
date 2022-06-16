from flask_sqlalchemy import SQLAlchemy
import click
from flask import current_app, g
from flask.cli import with_appcontext
import os

# from sqlalchemy import String, Integer

# Need to decide which one of these two database connection functions to use, if any! Might just use sqlitealchemy?
# Function 1

def get_db():
    """Get the SQLAlchemy database object"""
    if 'db' not in g:
        # Pass the application into SQLAlchemy object to create it
        g.db = SQLAlchemy(current_app)
    return g.db

def init_db():
    """Command that will be executed via CLI due to click"""
    db = get_db()
    engine = db.create_engine("sqlite:///"+os.path.join(current_app.instance_path, "weather.db"),{})
    meta = db.MetaData()
    engine.execute("DROP TABLE IF EXISTS users;")
    users = db.Table(
        "users", meta,
        db.Column("id", db.Integer, primary_key = True),
        db.Column("username", db.String, unique = True, nullable = False),
        db.Column("password_hashed", db.String, nullable = False),
        db.Column("username_check", db.String, nullable = False)
    )
    meta.create_all(engine)




@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear  existing data and create new tables"""
    init_db()
    click.echo("Initialized the database")

def init_app(app):
    app.cli.add_command(init_db_command)