import click
from flask import current_app, g
from flask.cli import with_appcontext
from datetime import datetime, timezone

from . import db

required_env_vars = (
    'DATABASE_HOST', 'DATABASE_INSTANCE', 'DATABASE_USER',
    'DATABASE_PASSWORD', 'ADMIN_USER', 'ADMIN_PASSWORD',
    'WORKER_HOSTNAME'
)

def get_dbclient(force=False):
    if 'client' not in g or force:
        close_dbclient()
        params = {}
        params['host'] = current_app.config.get('DATABASE_HOST')
        params['user'] = current_app.config.get('DATABASE_USER')
        params['db'] = current_app.config.get('DATABASE_INSTANCE')
        params['password'] = current_app.config.get('DATABASE_PASSWORD')
        g.client = db.DBClient(**params)
    return g.client


def get_host():
    if 'host' not in g:
        g.host = current_app.config.get('WORKER_HOSTNAME').replace('host_', '')


def close_dbclient(e=None):
    client = g.pop('client', None)
    if client is not None:
        client.close()


def init_db(drop_existing=False):
    client = get_dbclient()
    click.echo("PostgreSQL Connection -> \033[0;32mOK\033[0m")

    if not drop_existing:
        all_users, error = client.read("SELECT name from users;", all=True)
        if not error and all_users:
            click.echo("Application already init")
            return

    client = get_dbclient(force=True)

    admin_user = current_app.config['ADMIN_USER']
    admin_password = current_app.config['ADMIN_PASSWORD']
    worker_hostname = current_app.config['WORKER_HOSTNAME']
    current_datetime = datetime.now(timezone.utc)
    
    queries = [
        """
        DROP TABLE IF EXISTS users;
        """,
        """
        DROP TABLE IF EXISTS health_check;
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            admin BOOLEAN NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS health_check (
            id SERIAL PRIMARY KEY,
            hostname TEXT UNIQUE NOT NULL,
            last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """,
        f"""
        INSERT INTO users (name, password, admin) VALUES ('{admin_user}', '{admin_password}', TRUE);
        """,
        f"""
        INSERT INTO health_check (hostname, last_updated) VALUES ('{worker_hostname}', TIMESTAMP '{current_datetime}');
        """
    ]
    error = client.write(queries)
    if error:
        click.echo("Application init failed -> \033[0;31m%s\033[0m" % error)
    else:
        click.echo("Application initialized -> \033[0;32mOK\033[0m")


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create new tables and admin user if not existing."""
    init_db()


@click.command('force-init-db')
@with_appcontext
def force_init_db_command():
    """Drop existing tables and create new ones with admin user."""
    init_db(drop_existing=True)


def init_app(app):
    app.teardown_appcontext(close_dbclient)
    app.cli.add_command(init_db_command)
    app.cli.add_command(force_init_db_command)