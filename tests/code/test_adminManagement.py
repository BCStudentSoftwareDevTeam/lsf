import pytest
from app.controllers.admin_routes.adminManagement import addAdmin, removeAdmin
from app.models.user import User
from peewee import DoesNotExist

@pytest.mark.integration
def test_addAdmin():
    newAdmin = "pearcej"
    user = User.get(User.username == newAdmin)
    # Before adding user as admin
    assert not user.isLaborAdmin 
    # Test adding labor admin
    addAdmin(user, 'Labor')
    user = User.get(User.username == newAdmin)
    assert user.isLaborAdmin

    assert not user.isFinancialAidAdmin
    
    # Test adding financial aid admin
    addAdmin(user, 'FinancialAid')
    
    assert user.isFinancialAidAdmin

    assert not user.isSaasAdmin
    # Test adding saas admin
    addAdmin(user, 'Saas')
    assert user.isSaasAdmin
    
    # cleanup
    user.isLaborAdmin = False
    user.isFinancialAidAdmin = False
    user.isSaasAdmin = False
    user.save()

@pytest.mark.integration
def test_removeAdmin():
    oldAdmin = "pearcej"
    user = User.get(User.username == oldAdmin)
    addAdmin(user, 'Labor')
    # Before removing user as admin
    assert user.isLaborAdmin
    # Test removing labor admin
    removeAdmin(user, 'Labor')
    assert not user.isLaborAdmin

    addAdmin(user, 'FinancialAid')
    assert user.isFinancialAidAdmin
    # Test removing financial aid admin
    removeAdmin(user, 'FinancialAid')
    assert not user.isFinancialAidAdmin

    addAdmin(user, 'Saas')
    assert user.isSaasAdmin
    # Test removing saas admin
    removeAdmin(user, 'Saas')
    assert not user.isSaasAdmin
    

