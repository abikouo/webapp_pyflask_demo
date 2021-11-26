import os
from flask import (
    Flask, jsonify, current_app
)
import requests

def ping_server(host):
    if host == "" or host == None:
        return False
    print("Ping host: %s" % host)
    try:
        result = requests.get('http:://%s:5000/' % host)
        print('Ping host %s -> %s' % (host, result.status_code))
        return result.status_code == 200
    except Exception as e:
        print("Raise: %s" % e)
        return False

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Read application configuration
    app.config.from_mapping(WORKERS_CONFIG=os.environ["WORKERS_CONFIG"])

    @app.route('/', methods=['GET'])
    def home():
        return '''<h1>Rest api server</h1>
    <p>An API to ping active hosts from configuration.</p>'''


    # A route to return all of the available entries in our catalog.
    @app.route('/api/v1/hosts', methods=['GET'])
    def get():
        active_hosts = []
        try:
            config = current_app.config.get('WORKERS_CONFIG')
            with open(config) as f:
                active_hosts = list(filter(ping_server, f.read().split("\n")))
        except:
            active_hosts = []
        return jsonify(active_hosts)
    
    app.secret_key = 'ansible secret key'
    return app

def start_server():
    app = create_app()
    app.run(debug=True, host='0.0.0.0')