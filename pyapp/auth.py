import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from pyapp.appinit import get_dbclient

blue_print = Blueprint('auth', __name__)

@blue_print.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']

        error = None
        if not username:
            error = 'Name is required to create user.'
        elif not password:
            error = 'Password is required to create user.'

        if error is None:
            client = get_dbclient()
            error = client.write("INSERT INTO users (name, password, admin) VALUES ('%s', '%s', FALSE);" % (username, password))
            if error:
                error = "User creation failed: %s" % error
            else:
                message = f"User '{username}' successfully created."
                return redirect(url_for("auth.index"))

        flash(error)

    return render_template('auth/create.html')


@blue_print.route('/delete', methods=('GET', 'POST'))
def delete():
    if request.method == 'POST':
        username = request.form['name']

        error = None
        if not username:
            error = 'Name is required to delete user.'

        if error is None:
            client = get_dbclient()
            query = f"DELETE FROM users WHERE name='{username}';"
            error = client.write(query)
            if error:
                error = "User deletion failed: %s" % error
            else:
                message = f"User '{username}' successfully deleted."
                return redirect(url_for("auth.index"))
        flash(error)

    return render_template('auth/delete.html')

@blue_print.route('/find', methods=('GET', 'POST'))
def find():
    if request.method == 'POST':

        client = get_dbclient()
        all_users, error = client.read("SELECT name from users WHERE admin = 'no';", all=True)
        if not error:
            username = request.form['name']
            users = []
            if all_users:
                users = [x[0] for x in all_users]
                if username:
                    users = [x for x in all_users if re.match(username, x[0])]
                    if users == []:
                        users = [x for x in all_users if x[0] == username]
            return render_template("auth/index.html", users=users)

        flash(error)

    return render_template('auth/find.html')


@blue_print.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        
        client = get_dbclient()
        user, error = client.read("SELECT * from users WHERE name='%s';" % username)
        if not user:
            error = "user '%s' does not exist." % username
        else:
            if user[2] != password:
                error = "wrong password specified for user '%s'" % username
            else:
                session.clear()
                session['user_id'] = user[0]
                return redirect(url_for('auth.index'))
        flash(error)

    return render_template('auth/login.html')


@blue_print.before_app_request
def get_user_info():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        client = get_dbclient()
        user, error = client.read("SELECT * from users WHERE id=%s;" % user_id)
        g.user = {
            'id': user[0], 'name': user[1], 'password': user[2]
        }


@blue_print.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@blue_print.route("/")
def index():
    users = []
    return render_template("auth/index.html", users=users)
