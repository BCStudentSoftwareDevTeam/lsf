import pytest
from app.controllers.admin_routes.adminManagement import addAdmin, removeAdmin
from app.models.user import User
from app.models import mainDB
from peewee import DoesNotExist

@pytest.mark.integration
def test_addAdmin():
    with mainDB.atomic() as transaction:
        newAdmin = "pearcej"
        user = User.get(User.username == newAdmin)

        # Before adding user as admin
        assert not user.isLaborAdmin 
        addAdmin(user, 'Labor')
        user = User.get(User.username == newAdmin) # check if the db is actually changed
        assert user.isLaborAdmin

        assert not user.isFinancialAidAdmin
        addAdmin(user, 'FinancialAid')
        assert user.isFinancialAidAdmin

        assert not user.isSaasAdmin
        addAdmin(user, 'Saas')
        assert user.isSaasAdmin

@pytest.mark.integration
def test_removeAdmin():
    with mainDB.atomic() as transaction:
        oldAdmin = "pearcej"
        user = User.get(User.username == oldAdmin)

        assert user.isLaborAdmin
        removeAdmin(user, 'Labor')
        user = User.get(User.username == oldAdmin) # check if the db is actually changed
        assert not user.isLaborAdmin

        assert user.isFinancialAidAdmin
        removeAdmin(user, 'FinancialAid')
        assert not user.isFinancialAidAdmin

        assert user.isSaasAdmin
        removeAdmin(user, 'Saas')
        assert not user.isSaasAdmin
