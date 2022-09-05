from flask import render_template
from flask import Blueprint
from app.login_manager import require_login
import os

admin = Blueprint('admin', __name__)
@admin.context_processor
def injectGlobalData():
    currentUser = require_login()
    lastStaticUpdate = str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk('app/static')
                   for f in files))
    return {'currentUser': currentUser,
            'lastStaticUpdate': lastStaticUpdate}

from app.controllers.admin_routes import manage_departments
from app.controllers.admin_routes import termManagement
from app.controllers.admin_routes import adminManagement
from app.controllers.admin_routes import allPendingForms
from app.controllers.admin_routes import financialAidOverload
from app.controllers.admin_routes import emailTemplateController
