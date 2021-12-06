import os
from flask import Flask
import time
from . import appinit, auth, infra

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Read application configuration
    params = {}
    containerized = False
    for env_var in appinit.required_env_vars:
        if not env_var in os.environ:
            if env_var in ("WORKER_HOSTNAME", "WORKERS_HOSTS"):
                containerized = True
            else:
                raise ValueError("missing {0} from environment, unable to start server.".format(env_var))
        else:
            params[env_var] = os.environ[env_var]

    app.config.from_mapping(**params)

    app.secret_key = 'ansible secret key'

    appinit.init_app(app)

    app.register_blueprint(auth.blue_print)
    if not containerized:
        app.register_blueprint(infra.blue_print)

    app.add_url_rule("/", endpoint="index")

    return app

def start_server():
    app = create_app()
    app.run(debug=True, host='0.0.0.0')