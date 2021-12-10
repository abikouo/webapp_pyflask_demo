import time

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from pyapp.appinit import get_dbclient, get_host

blue_print = Blueprint('auth', __name__)

@blue_print.route('/create', methods=('GET', 'POST'))
def create():
    get_host()
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
            start = time.time()
            error = client.write("INSERT INTO users (name, password, admin) VALUES ('%s', '%s', FALSE);" % (username, password))
            elapsed = (time.time() - start) * 1000
            g.time = "%.2fms" % elapsed
            if error:
                error = "User creation failed: %s" % error
            else:
                error = f"User '{username}' successfully created."
            flash(error)
            return redirect(url_for("auth.index"))

        flash(error)

    return render_template('auth/create.html')


@blue_print.route('/delete', methods=('GET', 'POST'))
def delete():
    get_host()
    if request.method == 'POST':
        username = request.form['name']

        error = None
        if not username:
            error = 'Name is required to delete user.'

        if error is None:
            client = get_dbclient()
            query = f"DELETE FROM users WHERE name='{username}';"
            start = time.time()
            error = client.write(query)
            elapsed = (time.time() - start) * 1000
            g.time = "%.2fms" % elapsed
            if error:
                error = "User deletion failed: %s" % error
            else:
                error = f"User '{username}' successfully deleted."
            flash(error)
            return redirect(url_for("auth.index"))

        flash(error)

    return render_template('auth/delete.html')

@blue_print.route('/list', methods=('GET',))
def list():
    get_host()
    client = get_dbclient()
    start = time.time()
    all_users, error = client.read("SELECT name from users WHERE admin = 'no';", all=True)
    elapsed = (time.time() - start) * 1000
    g.time = "%.2fms" % elapsed
    if not error and all_users:
        users = [x[0] for x in all_users]
        return render_template("auth/list.html", users=users)
    
    flash(error)
    return redirect(url_for("auth.index"))


@blue_print.route('/login', methods=('GET', 'POST'))
def login():
    get_host()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        client = get_dbclient()
        start = time.time()
        user, error = client.read("SELECT * from users WHERE name='%s';" % username)
        elapsed = (time.time() - start) * 1000
        g.time = "%.2fms" % elapsed
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
        start = time.time()
        user, error = client.read("SELECT * from users WHERE id=%s;" % user_id)
        elapsed = (time.time() - start) * 1000
        g.time = "%.2fms" % elapsed
        if user:
            g.user = {
                'id': user[0], 'name': user[1], 'password': user[2]
            }


@blue_print.route('/logout')
def logout():
    get_host()
    session.clear()
    return redirect(url_for('index'))

@blue_print.route("/")
def index():
    users = []
    get_host()
    return render_template("head.html")
