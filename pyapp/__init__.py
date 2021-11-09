import os
from flask import Flask
import time
from . import appinit, auth, infra

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Read application configuration
    params = {}
    for env_var in appinit.required_env_vars:
        if not env_var in os.environ:
            raise ValueError("missing {0} from environment, unable to start server.".format(env_var))
        params[env_var] = os.environ[env_var]

    app.config.from_mapping(**params)

    app.secret_key = 'ansible secret key'

    appinit.init_app(app)

    app.register_blueprint(auth.blue_print)
    app.register_blueprint(infra.blue_print)

    app.add_url_rule("/", endpoint="index")

    return app

def start_server():
    pid = os.fork()

    if pid > 0:
        # parent process, listening server
        app = create_app()
        app.run(debug=True, host='0.0.0.0')
    
    else:
        # child process, send health check to the database
        params = {
            'dbhost': os.environ['DATABASE_HOST'],
            'dbname': os.environ['DATABASE_INSTANCE'],
            'db_user': os.environ['DATABASE_USER'],
            'db_user_password': os.environ['DATABASE_PASSWORD'],
            'hostname': os.environ['WORKER_HOSTNAME'],
        }
        
        while True:
            try:
                infra.send_health_check(**params)
                time.sleep(0.5)
            except Exception as e:
                print("send_health_check: %s" % e)