from sqlalchemy import Table,  Column, Integer, String, MetaData, ForeignKey, create_engine
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
        g.engine = create_engine("sqlite:///"+os.path.join(current_app.instance_path, "weather.db"))
        g.db = g.engine.connect()
    return g.db

def init_db():
    """Command that will be executed via CLI due to click"""
    engine = create_engine("sqlite:///"+os.path.join(current_app.instance_path, "weather.db"))
    meta = MetaData()
    engine.execute("DROP TABLE IF EXISTS users;")
    users = Table(
        "users", meta,
        Column("id", Integer, primary_key = True),
        Column("username", String, unique = True, nullable = False),
        Column("password_hashed", String, nullable = False),
        Column("username_check", String, nullable = False)
    )
    meta.create_all(engine)

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