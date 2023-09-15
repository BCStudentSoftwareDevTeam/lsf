from flask import Blueprint 

api_bp = Blueprint('error_routes', __name__)

from app.controllers.api_routes import routes