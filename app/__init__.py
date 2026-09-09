import os
from datetime import date

from flask import Flask
from flask_restful import Api
from flask_bootstrap import Bootstrap
from playhouse.shortcuts import model_to_dict, dict_to_model


app = Flask(__name__)
bootstrap = Bootstrap(app)
api = Api(app)

app.env = os.environ.get('APP_ENV', 'production')
from app.config.loadConfig import get_secret_cfg
app.config.update(get_secret_cfg())
print (" * Environment:", app.env)
app.config['ENV'] = app.env

app.secret_key = app.config["secret_key"]

app.config['use_shibboleth'] = (app.config['ENV'] == 'production')
app.config['use_tracy'] = (app.config['ENV'] in ('production','staging'))
if 'use_banner' not in app.config.keys():
    app.config['use_banner'] = (app.config['ENV'] in ('production','staging'))

# Record and output queries if requested
from flask import session
from peewee import BaseQuery
if app.config.get('show_queries'):
    old_execute = BaseQuery.execute
    def new_execute(*args, **kwargs):
        if session:
            if 'querycount' not in session:
                session['querycount'] = 0

            session['querycount'] += 1
            if app.config.get('show_queries'): # in case we selectively disable
                print("**Running query {}**".format(session['querycount']))
                print(args[0])
        return old_execute(*args, **kwargs)
    BaseQuery.execute = new_execute

# Registers blueprints (controllers). These are general routes, like /index
from app.controllers.main_routes import main_bp as main_bp
app.register_blueprint(main_bp)

# Registers the admin interface blueprints
from app.controllers.admin_routes import admin as admin_bp
app.register_blueprint(admin_bp)

# Registers error messaging
from app.controllers.errors_routes import error as errors_bp
app.register_blueprint(errors_bp)

from app.controllers.api_routes.routes import initializeApiRoutes
initializeApiRoutes(api)

from flask import g
from app.models.user import User
from app.login_manager import require_login
@app.before_request
def load_user():
    try: 
        g.currentUser = dict_to_model(User, session['currentUser'])
    except Exception as e:
        user = require_login()
        session['currentUser'] = model_to_dict(user)
        g.currentUser = user

from app.models.term import Term
from app.login_manager import getOpenTerm
@app.before_request
def load_openTerm():
    try: 
        g.openTerm = dict_to_model(Term, session['openTerm'])
    except Exception as e:
        term = getOpenTerm()
        if term:
            session['openTerm'] = model_to_dict(term)
        g.openTerm = term

def getCurrentAY():
    """
    Returns the current academic year as a tuple 
    (the year when it starts, and the year when it ends)
    """
    today = date.today()
    year = today.year

    if today.month < 7:
        return year - 1, year

    return year, year + 1

@app.before_request
def load_currentAY():
    g.currentAY = getCurrentAY()
        
@app.context_processor
def inject_environment():
    return dict(env=app.config['ENV'])

@app.before_request
def queryCount():
    if session:
        session['querycount'] = 0