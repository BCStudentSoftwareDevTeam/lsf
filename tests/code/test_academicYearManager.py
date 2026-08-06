import pytest

from flask import g
from app.models.term import *

from app.logic.academicYearManager import * 

@pytest.mark.integration
def test_getCurrentAndNextAY():
    with app.app_context():
        g.currentYear = (1967, 1968)
        currentYear, nextYear = getCurrentAndNextAY()
        
        assert currentYear.termCode == 196700
        assert currentYear.termName == "AY 1967-1968"

        assert nextYear.termCode == 196800
        assert nextYear.termName == "AY 1968-1969"


        g.currentYear = (2102, 2103)
        currentYear, nextYear = getCurrentAndNextAY()
        
        assert currentYear.termCode == 210200
        assert currentYear.termName == "AY 2102-2103"

        assert nextYear.termCode == 210300
        assert nextYear.termName == "AY 2103-2104"

        # Testing data types 
        assert isinstance(currentYear.termCode, int)
        assert isinstance(nextYear.termCode, int)

        assert isinstance(currentYear.termName, str)
        assert isinstance(nextYear.termName, str)
        
        # Testing whether termName is formatted correctly
        assert currentYear.termName.split(" ")[0] == "AY"
        assert nextYear.termName.split(" ")[0] == "AY"

        assert currentYear.termName.split(" ")[1] == "2102-2103"
        assert nextYear.termName.split(" ")[1] == "2103-2104"