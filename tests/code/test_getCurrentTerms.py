import pytest
from app import app

from app.models.term import Term
from app.logic.getCurrentTerms import getCurrentTerms
from datetime import datetime, date

@pytest.fixture
def test_terms():

    currentYear = date.today().year - 12
    print(currentYear)

    test_currentAY = Term.create(
        termCode = f"{currentYear}00",
        termName = f"AY {currentYear}-2001",
        termStart = f"{currentYear}-08-01",
        termEnd = f"{currentYear + 1}-05-01",
        termState = 1,
        primaryCutOff = f"{currentYear + 1}-09-01",
        adjustmentCutOff = f"2002-10-01"
        )
    test_fallTerm = Term.create(
            termCode = f"{currentYear}11",
            termName = f"Fall {currentYear}",
            termStart = f"{currentYear}-08-01",
            termEnd = f"{currentYear}-12-12",
            termState = 1,
            primaryCutOff = f"{currentYear}-09-01",
            adjustmentCutOff = f"{currentYear}-10-01"
            )
    test_springTerm = Term.create(
            termCode = f"{currentYear}12",
            termName = f"Spring {currentYear + 1}",
            termStart = f"{currentYear + 1}-01-01",
            termEnd = f"{currentYear + 1}-05-01",
            termState = 1,
            primaryCutOff = f"{currentYear + 1}-02-01",
            adjustmentCutOff = f"{currentYear + 1}-3-01"
            )
    yield test_currentAY, test_fallTerm, test_springTerm

    #destroy all created data
    test_currentAY.delete_instance()
    test_fallTerm.delete_instance()
    test_springTerm.delete_instance()

@pytest.mark.integration
def test_getCurrentTerms(test_terms):
    currentAY, fallTerm, springTerm = getCurrentTerms()
    assert currentAY != test_terms[0]
    assert fallTerm != test_terms[1]
    assert springTerm != test_terms[2]
    
    return 1