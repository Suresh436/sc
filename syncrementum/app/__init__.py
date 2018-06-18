from functools import wraps

import flask
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import create_engine
from werkzeug.contrib.fixers import ProxyFix
from flask_login import LoginManager, current_user
from flask import Flask, session, url_for, request
from flask_cors import CORS
from flask import Flask
from flask_recaptcha import ReCaptcha
import datetime

from werkzeug.utils import redirect

app = Flask(__name__)

CORS(app)

app.wsgi_app = ProxyFix(app.wsgi_app)

# Setup the app with the config.py file
app.config.from_pyfile('config.py')

# Setup the database
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
# Setup the mail server
from flask_mail import Mail
mail = Mail(app)
from app.models import User


# Setup the logger
from app.logger_setup import logger

# Setup the debug toolbar
from flask_debugtoolbar import DebugToolbarExtension
app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
app.config['DEBUG_TB_PROFILER_ENABLED'] = True
toolbar = DebugToolbarExtension(app)

# Import the views
from app.views import (main, user, cron, targets, payment, settings)

app.register_blueprint(user.userbp)
app.register_blueprint(cron.cronbp)
app.register_blueprint(targets.targetsbp)
app.register_blueprint(payment.paymentbp)
app.register_blueprint(settings.settingsbp)
auth = HTTPBasicAuth()

# Setup the user login process
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'userbp.user_signin'


@login_manager.user_loader
def load_user(uid):
    return User.query.filter(User.id == uid).first()


@app.context_processor
def all_users():
    user_size = 10
    start_id = 0
    start, stop = user_size * start_id, user_size * (start_id + 1)
    offset_start = {'start': start, 'stop': stop}
    #allusers = User.all_users(offset_start)
    get_uid = request.args.get('userid', default=None, type=int)
    if get_uid is not None:
        user_details = User.by_id(get_uid)
    else:
        user_details = current_user
    return dict(get_uid=get_uid, user_details=user_details)

