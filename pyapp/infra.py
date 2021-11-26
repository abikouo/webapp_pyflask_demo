import json
from flask import (
    Blueprint, flash, render_template, current_app
)
import requests

blue_print = Blueprint('infra', __name__)

def ping_controller():
    try:
        response = requests.get("%s:5000/api/v1/hosts" % current_app.config.get("CONTROLLER_HOST"))
        print("Response: %s" % response.status_code)
        if response.status_code == 200:
            return json.loads(response.content), None
        else:
            return None, None
    except Exception as err:
        return None, err


@blue_print.route('/display', methods=('GET',))
def display():
    workers = []
    try:
        response = requests.get("%s:5000/api/v1/hosts" % current_app.config.get("CONTROLLER_HOST"))
        if response.status_code == 200:
            workers = json.loads(response.content)
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