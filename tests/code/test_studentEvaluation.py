import pytest
from app.controllers.main_routes.studentLaborEvaluation import sle
from app import app
import pytest
from app.models import mainDB
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
import json


@pytest.mark.integration
def testCreateStudentEval():
    with mainDB.atomic() as transaction:

        with app.test_request_context(
            "/sle", method="POST", data=termCodeDict):
                createSLEform = sle()

                transaction.rollback()
