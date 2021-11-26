import json
from flask import (
    Blueprint, flash, render_template, current_app
)
import requests

blue_print = Blueprint('infra', __name__)

@blue_print.route('/display', methods=('GET',))
def display():
    workers = []
    try:
        for h in current_app.config.get("WORKERS_HOSTS").split(","):
            if h == "":
                continue
            v = h.split(":")
            if v[0] == current_app.config.get("WORKER_HOSTNAME"):
                workers.append(v[0])
            else:
                response = requests.get("http://%s:5000/" % v[1])
                if response.status_code == 200:
                    workers.append(v[0])
    except Exception as err:
        flash(err)
    return render_template("infra/display.html",
                            active_workers=0,
                            workers=workers,
                            database={
                                'host': "%s.postgres.database.azure.com" % current_app.config.get('DATABASE_HOST'),
                                'instance': current_app.config.get('DATABASE_INSTANCE'),
                            }
                        )
