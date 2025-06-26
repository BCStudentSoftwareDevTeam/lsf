from app.controllers.main_routes import *
from app.models.user import *
from app.models.laborStatusForm import *
from app.models.term import *
from flask_bootstrap import bootstrap_find_resource
from app.models.Tracy.studata import *
from app import *
from app.login_manager import *
from app.config.loadConfig import load_config

@app.context_processor
def injectGlobalData():
    currentUser = require_login()
    lastStaticUpdate = str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk('app/static')
                   for f in files))
    return {'currentUser': currentUser,
            'lastStaticUpdate': lastStaticUpdate}

@app.route("/contributors", methods = ["GET"])
def contributors():
    currentUser = require_login()
    if not currentUser:        # Not logged in
        return render_template('errors/403.html'), 403

    contribs = load_config("app/config/contributors.yaml")
    return render_template("main/contributors.html",
           cfg = contribs
           )
