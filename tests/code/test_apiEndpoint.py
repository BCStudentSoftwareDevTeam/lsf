import pytest

from app import app
from app.logic.apiEndpoint import getLaborInformation

@pytest.mark.integration
def test_getLaborInformation():
    with app.test_request_context():

        bla = getLaborInformation(bNumber = "B00841417")
        print(bla)