import pytest

from flask import request, g
from werkzeug.datastructures import ImmutableMultiDict

from app import app
from app.models.allocation import Allocation
from app.models import mainDB
from app.models.term import Term

from app.logic.allocationRequest import *


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.integration
def test_getOrUpdateRequestedAllocation(client):
    with app.test_request_context('/allocationRequest/submit', method='POST', data={
        'submitter': "2",
        'breakHours': "750",
        'primary_10': "4",
        'primary_12': "13",
        'primary_15': "7",
        'primary_20': "5",
        'secondary_5': "2",
        'secondary_10': "0",
        'breakHours': "100",
        'justification': ""
    }):
        with mainDB.atomic() as transaction:
            g.openTerm, _ = Term.get_or_create(
                termCode=200200,
                defaults={"termName": "AY 2002-2003", "isAcademicYear": True}
            )

            currentAlloc = Allocation.create(
                termCode=200200,
                department=2,
                isFinal=True,
                justification="",
                primary_10=12,
                primary_12=3,
                primary_15=4,
                primary_20=5,
                secondary_5=1,
                secondary_10=3,
                breakHours=399
            )

            nextYear = Term.create(termCode=200300)

            getOrUpdateRequestedAllocation()

            allocation = Allocation.get(Allocation.termCode == g.openTerm.termCode + 100, Allocation.department == request.form.get("submitter", type=int, default=None))
            
            assert isinstance(allocation.termCode, Term)
            assert isinstance(allocation.termCode.termCode, int)
            assert allocation.termCode.termCode == 200300

            assert isinstance(allocation.department, Department)
            assert isinstance(allocation.department.departmentID, int)
            assert allocation.department.departmentID == 2

            assert isinstance(allocation.isFinal, bool)
            assert allocation.isFinal == False

            assert isinstance(allocation.justification, str)
            assert allocation.justification == ""
            
            assert isinstance(allocation.primary_10, int)
            assert allocation.primary_10 == 4
            
            assert isinstance(allocation.primary_12, int)
            assert allocation.primary_12 == 13
            
            assert isinstance(allocation.primary_15, int)
            assert allocation.primary_15 == 7

            assert isinstance(allocation.primary_20, int)
            assert allocation.primary_20 == 5

            assert isinstance(allocation.secondary_5, int)
            assert allocation.secondary_5 == 2

            assert isinstance(allocation.secondary_10, int)
            assert allocation.secondary_10 == 0

            assert isinstance(allocation.breakHours, int)
            assert allocation.breakHours == 100

            transaction.rollback()