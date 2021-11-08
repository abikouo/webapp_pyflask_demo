from datetime import datetime, timezone

from flask import (
    Blueprint, flash, render_template, current_app
)

from pyapp.appinit import get_dbclient
from pyapp.db import DBClient

blue_print = Blueprint('infra', __name__)

@blue_print.route('/display', methods=('GET',))
def display():
    client = get_dbclient()
    workers, error = client.read("SELECT hostname, last_updated from health_check;", all=True)
    if not error:
        current_datetime = datetime.now(timezone.utc).replace(tzinfo=None)
        workers_up = []
        workers_down = []
        for row in workers:
            age = (current_datetime - row[1]).seconds
            if age < 5:
                workers_up.append(row[0])
            else:
                workers_down.append({
                    'name': row[0], 'down_time': age
                })
        db_info = {
            'host': current_app.config.get('DATABASE_HOST'),
            'dbname': current_app.config.get('DATABASE_INSTANCE'),
        }
        return render_template("infra/display.html", workers_up=workers_up, workers_down=workers_down, dbinfo=db_info)

    flash(error)


def send_health_check(dbhost, dbname, db_user, db_user_password, hostname):
    if not send_health_check.client:
        send_health_check.client = DBClient(host=dbhost, user=db_user, db=dbname, password=db_user_password)
    
    current_datetime = datetime.now(timezone.utc)
    query = f"UPDATE health_check SET last_updated = TIMESTAMP '{current_datetime}' WHERE hostname = '{hostname}';"
    error = send_health_check.client.write(query)
    if error:
        print(error)
    else:
        print(f"Health check ({hostname}) at ({current_datetime}) => \033[;32mOK\033[0m")

send_health_check.client = None