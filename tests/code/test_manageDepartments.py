import pytest
import json

from werkzeug.exceptions import BadRequest
from unittest.mock import patch

from flask import g 
from flask_wtf.csrf import CSRFProtect

from app import app

from app.models import mainDB
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.term import Term
from app.models.formHistory import FormHistory
from app.models.allocation import Allocation

from app.controllers.admin_routes import manageDepartments

from app.logic.manageDepartments import *


# The following test file is for testing the manageDepartments logic file and its associated functions and queries. 
# It is designed to ensure that the manageDepartments functionality works as expected and returns the correct data.


@pytest.mark.integration
def test_generateAdjacentYears():
    with app.app_context():
        with mainDB.atomic() as transaction:

            ################ THE FIRST TEST ################ 
            ################ TESTING WHETHER THE generateAdjacentYear() FUNCTION WORKS AT ALL
            g.openTerm, _ = Term.get_or_create(
                termCode = 202500,
                defaults={"termName": "AY 2025-2026", "isAcademicYear": True}
            )
            
            # 
            currentYear, previousYear, followingYear = generateAdjacentYears(202500)
            
            assert currentYear.termCode == 202500
            assert currentYear.termName == "AY 2025-2026"

            assert previousYear.termCode == 202400
            assert previousYear.termName == "AY 2024-2025"

            assert followingYear.termCode == 202600
            assert followingYear.termName == "AY 2026-2027"


            ################ THE SECOND TEST ################
            ######### TESTING VARIOUS EDGE CASES ############
            with pytest.raises(BadRequest):
                generateAdjacentYears(202300)
                transaction.rollback()

            with pytest.raises(BadRequest):
                generateAdjacentYears(202200)
                transaction.rollback()

            with pytest.raises(BadRequest):
                generateAdjacentYears(2025)
                transaction.rollback()
            
            with pytest.raises(BadRequest):
                generateAdjacentYears(True)
                transaction.rollback()

            with pytest.raises(BadRequest):
                generateAdjacentYears(False)
                transaction.rollback()

            with pytest.raises(BadRequest):
                generateAdjacentYears("SELECT lsf DELETE *")
                transaction.rollback()


            ################ THE THIRD TEST ################
            ############# MISCELLANEOUS TESTS #############
            g.openTerm, _ = Term.get_or_create(
                termCode = 198200,
                defaults={"termName": "AY 1982-1983", "isAcademicYear": True}
            )

            # Testing different years
            currentYear, previousYear, followingYear = generateAdjacentYears(198200)
            
            assert currentYear.termCode == 198200
            assert currentYear.termName == "AY 1982-1983"

            assert previousYear.termCode == 198100
            assert previousYear.termName == "AY 1981-1982"

            assert followingYear.termCode == 198300
            assert followingYear.termName == "AY 1983-1984"

            # Testing data types 
            assert isinstance(currentYear.termCode, int)
            assert isinstance(previousYear.termCode, int)
            assert isinstance(followingYear.termCode, int)
            
            # Testing whether currentYear.termName is formatted correctly
            assert currentYear.termName.split(" ")[0] == "AY"
            assert previousYear.termName.split(" ")[0] == "AY"
            assert followingYear.termName.split(" ")[0] == "AY"

            assert currentYear.termName.split(" ")[1] == "1982-1983"
            assert previousYear.termName.split(" ")[1] == "1981-1982"
            assert followingYear.termName.split(" ")[1] == "1983-1984"


            # Testing the generateAdjacentYears() function without any parameters
            currentYear, previousYear, followingYear = generateAdjacentYears()

            assert currentYear.termCode == 198200
            assert previousYear.termCode == 198100
            assert followingYear.termCode == 198300

            transaction.rollback()