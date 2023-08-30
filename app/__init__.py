from flask import Flask
import yaml
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *


app = Flask(__name__)
bootstrap = Bootstrap(app)
# login = LoginManager(app)  #FIXME: needs configured with our dev/prod environment handlers

def load_config(file):
    with open(file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return cfg

cfg = load_config("app/config/secret_config.yaml")
app.secret_key = cfg["secret_key"]

app.config['use_shibboleth'] = False
if app.config['ENV'] == 'production':
    app.config['use_shibboleth'] = True

app.config['use_tracy'] = False
if app.config['ENV'] in ('production','staging'):
    app.config['use_tracy'] = True

app.config['use_banner'] = False
if app.config['ENV'] in ('production','staging'):
    app.config['use_banner'] = True

# Record and output queries if requested
app.config['show_queries'] = cfg["show_queries"] if "show_queries" in cfg else False
from flask import session
from peewee import BaseQuery
if app.config['show_queries']:
    old_execute = BaseQuery.execute
    def new_execute(*args, **kwargs):
        if session:
            if 'querycount' not in session:
                session['querycount'] = 0

            session['querycount'] += 1
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

from app.logic.orgPositionEndpoint import getFormsForOrg
from app.models.department import Department
@app.route('/api/org/<orgCode>', methods=['GET'])
def getLaborForms(orgCode):
    # TODO: Need to add authentication
    if Department.select(Department.ORG == orgCode).exists(): 
        return getFormsForOrg(orgCode)
    else: 
        print("########## YOU FUCKED UP ##########")

@app.context_processor
def inject_environment():
    return dict(env=app.config['ENV'])

@app.before_request
def queryCount():
    if session:
        session['querycount'] = 0

