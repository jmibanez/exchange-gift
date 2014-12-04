import logging.config
import yaml

import os
import sys

sys.path.insert(0, 'libs')
sys.path.insert(0, 'libs.zip')

from flask import Flask, request, abort, jsonify
from gifts2.routes import web, admin
from flask.ext.bootstrap import Bootstrap
from flask.ext.babel import Babel

from google.appengine.api.app_identity import get_application_id
from google.appengine.api import modules

app = Flask(__name__)
Bootstrap(app)
babel = Babel(app)

app.config['BOOTSTRAP_USE_MINIFIED'] = True
app.config['BOOTSTRAP_USE_CDN'] = True
app.config['BOOTSTRAP_FONTAWESOME'] = True
app.config['SECRET_KEY'] = 'devkey'
app.config['CSRF_ENABLED'] = True
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Manila'

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(web)

# Configure logging
with open('res/log-config.yaml', 'r') as f:
    log_config = yaml.load(f)
log_config.setdefault('version', 1)
logging.config.dictConfig(log_config)

