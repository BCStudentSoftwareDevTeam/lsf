import pytest

from app.models import mainDB
from app.models.allocation import Allocation
from app.models.laborStatusForm import * 
from app.models.department import *
from app.models.term import *
from app.models.formHistory import FormHistory

from app.logic.allocationManager import *