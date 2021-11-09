from datetime import datetime, timezone

from flask import (
    Blueprint, flash, render_template, current_app
)

from pyapp.appinit import get_dbclient, get_host
from pyapp.db import DBClient

blue_print = Blueprint('infra', __name__)

@blue_print.route('/display', methods=('GET',))
def display():
    get_host()
    client = get_dbclient()
    workers, error = client.read("SELECT hostname, last_updated from health_check;", all=True)
    print("workers = %s error = %s" % (workers, error))
    if not error:
        current_datetime = datetime.now(timezone.utc).replace(tzinfo=None)
        workers_up = []
        workers_down = []
        if workers:
            for row in workers:
                age = (current_datetime - row[1]).seconds
                if age < 5:
                    workers_up.append(row[0])
                else:
                    workers_down.append({
                        'name': row[0], 'down_time': age
                    })
        db_info = {
            'host': "%s.postgres.database.azure.com" % current_app.config.get('DATABASE_HOST'),
            'instance': current_app.config.get('DATABASE_INSTANCE'),
        }
        print("workers = %s" % workers_up)
        return render_template("infra/display.html", workers=workers_up, database=db_info)

    flash(error)


def send_health_check(dbhost, dbname, db_user, db_user_password, hostname):
    if not send_health_check.client:
        send_health_check.client = DBClient(host=dbhost, user=db_user, db=dbname, password=db_user_password)

    def _exists():
        client = DBClient(host=dbhost, user=db_user, db=dbname, password=db_user_password)
        qry = f"SELECT hostname from health_check WHERE hostname = '{hostname}';"
        entry, error = send_health_check.client.read(qry)
        client.close()
        return entry is not None

    # Search existing entry
    query = f"SELECT hostname from health_check WHERE hostname = '{hostname}';"
    last_update = datetime.now(timezone.utc)
    query = f"UPDATE health_check SET last_updated = TIMESTAMP '{last_update}' WHERE hostname = '{hostname}';"
    if not _exists():
        query = f"INSERT INTO health_check (hostname, last_updated) VALUES ('{hostname}', TIMESTAMP '{last_update}');"

    error = send_health_check.client.write(query)
    if error:
        print(error)


send_health_check.client = None