import pytest
import json
from werkzeug.exceptions import BadRequest

from flask import g 
from flask_wtf.csrf import CSRFProtect

from app import app
from app.models import mainDB
from app.models.term import Term
from app.controllers.admin_routes import manageDepartments

from app.logic.manageDepartments import *


# The following test file is for testing the manageDepartments logic file and its associated functions and queries. 
# It is designed to ensure that the manageDepartments functionality works as expected and returns the correct data.