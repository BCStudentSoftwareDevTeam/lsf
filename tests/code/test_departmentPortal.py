import pytest

from types import SimpleNamespace
from unittest.mock import MagicMock
from flask import Flask, g

import app.controllers.main_routes.departmentPortal as department_portal


@pytest.fixture
def app():
    """
    Creates a small Flask application for testing the department portal routes.
    """
    test_app = Flask(__name__)

    test_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        CURRENT_USER=None,
    )

    @test_app.before_request
    def load_test_current_user():
        g.currentUser = test_app.config["CURRENT_USER"]

    test_app.register_blueprint(department_portal.main_bp)

    return test_app


@pytest.fixture
def client(app):
    """
    Creates a Flask test client.
    """
    return app.test_client()


def setCurrentUser(client, user):
    client.application.config["CURRENT_USER"] = user


def fakeAdminUser():
    return SimpleNamespace(
        supervisor=SimpleNamespace(ID="B00000099"),
        student=None,
        isLaborAdmin=True,
        isLaborDepartmentStudent=False,
    )


def fakeLaborDepartmentStudentUser():
    return SimpleNamespace(
        supervisor=SimpleNamespace(ID="B00000098"),
        student=None,
        isLaborAdmin=False,
        isLaborDepartmentStudent=True,
    )


def fakeSupervisorUser():
    return SimpleNamespace(
        supervisor=SimpleNamespace(ID="B00000001"),
        student=None,
        isLaborAdmin=False,
        isLaborDepartmentStudent=False,
    )


# -------------------------------------------------------------------
# manageMembers tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_manage_members_for_supervisor(client, monkeypatch):
    fake_supervisor = SimpleNamespace(
        ID="B00000001",
        legal_name="Test Supervisor",
    )

    fake_user = SimpleNamespace(
        supervisor=fake_supervisor,
        student=None,
        isLaborAdmin=False,
        isLaborDepartmentStudent=False,
    )

    fake_department = SimpleNamespace(
        departmentID=10,
        ORG=2114,
        ACCOUNT="60000",
        DEPT_NAME="Computer Science",
    )

    fake_members = [
        SimpleNamespace(
            supervisor=SimpleNamespace(
                ID="B00000002",
                LAST_NAME="Scott",
            )
        )
    ]

    fake_counts = {
        ("10", "B00000002"): {
            "active_primary_positions": 3,
        },
    }

    fake_members_with_counts = [
        SimpleNamespace(
            supervisor=SimpleNamespace(
                ID="B00000002",
                LAST_NAME="Scott",
            ),
            active_primary_positions=3,
        )
    ]

    setCurrentUser(client, fake_user)

    monkeypatch.setattr(
        department_portal,
        "getCurrentDepartment",
        lambda org, account: fake_department,
    )

    monkeypatch.setattr(
        department_portal,
        "getDepartmentMembers",
        lambda department: fake_members,
    )

    monkeypatch.setattr(
        department_portal,
        "getStudentCounts",
        lambda department: fake_counts,
    )

    monkeypatch.setattr(
        department_portal,
        "attachPositionCounts",
        lambda members, counts: fake_members_with_counts,
    )

    monkeypatch.setattr(
        department_portal,
        "currentAcademicYear",
        lambda: "2026-2027",
    )

    render_mock = MagicMock(return_value="Manage Members Page")

    monkeypatch.setattr(
        department_portal,
        "render_template",
        render_mock,
    )

    response = client.get(
        "/department/2114/60000/members"
    )

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Manage Members Page"

    render_mock.assert_called_once_with(
        "main/manageMembers.html",
        members=fake_members_with_counts,
        department=fake_department,
        currentAcademicYear="2026-2027",
    )


@pytest.mark.integration
def test_manage_members_redirects_student(client, monkeypatch):
    fake_student = SimpleNamespace(
        ID="B00000100",
    )

    fake_user = SimpleNamespace(
        supervisor=None,
        student=fake_student,
        isLaborAdmin=False,
        isLaborDepartmentStudent=False,
    )

    setCurrentUser(client, fake_user)

    monkeypatch.setattr(
        department_portal,
        "url_for",
        lambda endpoint, **values:
            f"/laborhistory/{values['id']}",
    )

    response = client.get(
        "/department/2114/60000/members"
    )

    assert response.status_code == 302
    assert response.location.endswith(
        "/laborhistory/B00000100"
    )


# -------------------------------------------------------------------
# searchMember tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_search_member_by_bnumber(client, monkeypatch):
    fake_user = fakeAdminUser()

    fake_database_supervisor = SimpleNamespace(
        ID="B00000002",
    )

    fake_query = MagicMock()
    fake_query.order_by.return_value = fake_query
    fake_query.limit.return_value = [
        fake_database_supervisor,
    ]

    search_mock = MagicMock(return_value=fake_query)

    setCurrentUser(client, fake_user)

    monkeypatch.setattr(
        department_portal,
        "searchPerson",
        search_mock,
    )

    monkeypatch.setattr(
        department_portal,
        "supervisorsDbToDict",
        lambda supervisor: {
            "bnumber": supervisor.ID,
            "firstName": "John",
            "lastName": "Scott",
        },
    )

    response = client.get(
        "/members/search/B00000002"
    )

    assert response.status_code == 200

    assert response.get_json() == [
        {
            "bnumber": "B00000002",
            "firstName": "John",
            "lastName": "Scott",
        }
    ]

    search_mock.assert_called_once_with(
        department_portal.Supervisor,
        "B00000002",
    )


@pytest.mark.integration
def test_search_member_by_single_name(client, monkeypatch):
    fake_user = fakeAdminUser()

    fake_database_supervisor = SimpleNamespace(
        ID="B00000003",
    )

    fake_query = MagicMock()
    fake_query.order_by.return_value = fake_query
    fake_query.limit.return_value = [
        fake_database_supervisor,
    ]

    search_mock = MagicMock(return_value=fake_query)

    setCurrentUser(client, fake_user)

    monkeypatch.setattr(
        department_portal,
        "searchPerson",
        search_mock,
    )

    monkeypatch.setattr(
        department_portal,
        "supervisorsDbToDict",
        lambda supervisor: {
            "bnumber": supervisor.ID,
            "firstName": "Mary",
            "lastName": "Johnson",
        },
    )

    response = client.get(
        "/members/search/Mary"
    )

    assert response.status_code == 200

    assert response.get_json() == [
        {
            "bnumber": "B00000003",
            "firstName": "Mary",
            "lastName": "Johnson",
        }
    ]

    search_mock.assert_called_once_with(
        department_portal.Supervisor,
        "Mary",
    )


@pytest.mark.integration
def test_search_member_by_full_name(client, monkeypatch):
    fake_user = fakeAdminUser()

    fake_database_supervisor = SimpleNamespace(
        ID="B00000004",
    )

    fake_query = MagicMock()
    fake_query.order_by.return_value = fake_query
    fake_query.limit.return_value = [
        fake_database_supervisor,
    ]

    search_mock = MagicMock(return_value=fake_query)

    setCurrentUser(client, fake_user)

    monkeypatch.setattr(
        department_portal,
        "searchPerson",
        search_mock,
    )

    monkeypatch.setattr(
        department_portal,
        "supervisorsDbToDict",
        lambda supervisor: {
            "bnumber": supervisor.ID,
            "firstName": "James",
            "lastName": "Smith",
        },
    )

    response = client.get(
        "/members/search/James%20Smith"
    )

    assert response.status_code == 200

    assert response.get_json() == [
        {
            "bnumber": "B00000004",
            "firstName": "James",
            "lastName": "Smith",
        }
    ]

    search_mock.assert_called_once_with(
        department_portal.Supervisor,
        "James Smith",
    )


@pytest.mark.integration
def test_search_member_returns_empty_list(client, monkeypatch):
    fake_user = fakeAdminUser()

    fake_query = MagicMock()
    fake_query.order_by.return_value = fake_query
    fake_query.limit.return_value = []

    search_mock = MagicMock(return_value=fake_query)

    setCurrentUser(client, fake_user)

    monkeypatch.setattr(
        department_portal,
        "searchPerson",
        search_mock,
    )

    response = client.get(
        "/members/search/Unknown"
    )

    assert response.status_code == 200
    assert response.get_json() == []

    search_mock.assert_called_once_with(
        department_portal.Supervisor,
        "Unknown",
    )


@pytest.mark.integration
def test_search_member_allows_labor_department_student(
    client,
    monkeypatch,
):
    fake_user = fakeLaborDepartmentStudentUser()

    fake_query = MagicMock()
    fake_query.order_by.return_value = fake_query
    fake_query.limit.return_value = []

    search_mock = MagicMock(return_value=fake_query)

    setCurrentUser(client, fake_user)

    monkeypatch.setattr(
        department_portal,
        "searchPerson",
        search_mock,
    )

    response = client.get(
        "/members/search/Unknown"
    )

    assert response.status_code == 200
    assert response.get_json() == []


@pytest.mark.integration
def test_search_member_returns_403_for_unauthorized_user(
    client,
    monkeypatch,
):
    fake_user = fakeSupervisorUser()

    setCurrentUser(client, fake_user)

    monkeypatch.setattr(
        department_portal,
        "render_template",
        lambda template: "Forbidden",
    )

    response = client.get(
        "/members/search/Scott"
    )

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Forbidden"


# -------------------------------------------------------------------
# updateCoordinator tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_update_coordinator_assigns_coordinator(
    client,
    monkeypatch,
):
    fake_member = SimpleNamespace(
        isCoordinator=False,
        save=MagicMock(),
    )

    setCurrentUser(client, fakeAdminUser())

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get",
        lambda *args, **kwargs: fake_member,
    )

    response = client.post(
        "/members/update_coordinator",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
            "isCoordinator": "true",
        },
    )

    assert response.status_code == 200
    assert fake_member.isCoordinator is True
    fake_member.save.assert_called_once()


@pytest.mark.integration
def test_update_coordinator_removes_coordinator(
    client,
    monkeypatch,
):
    fake_member = SimpleNamespace(
        isCoordinator=True,
        save=MagicMock(),
    )

    setCurrentUser(client, fakeAdminUser())

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get",
        lambda *args, **kwargs: fake_member,
    )

    response = client.post(
        "/members/update_coordinator",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
            "isCoordinator": "false",
        },
    )

    assert response.status_code == 200
    assert fake_member.isCoordinator is False
    fake_member.save.assert_called_once()


@pytest.mark.integration
def test_update_coordinator_requires_department_id(
    client,
):
    setCurrentUser(client, fakeAdminUser())

    response = client.post(
        "/members/update_coordinator",
        data={
            "supervisorID": "B00000001",
            "isCoordinator": "true",
        },
    )

    assert response.status_code == 400


@pytest.mark.integration
def test_update_coordinator_requires_permission(
    client,
    monkeypatch,
):
    setCurrentUser(client, fakeSupervisorUser())

    monkeypatch.setattr(
        department_portal,
        "render_template",
        lambda template: "Forbidden",
    )

    response = client.post(
        "/members/update_coordinator",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
            "isCoordinator": "true",
        },
    )

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Forbidden"


# -------------------------------------------------------------------
# eligibility tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_update_eligibility_bans_supervisor(
    client,
    monkeypatch,
):
    fake_supervisor = SimpleNamespace(
        ID="B00000001",
        isBanned=False,
        save=MagicMock(),
    )

    setCurrentUser(client, fakeAdminUser())

    monkeypatch.setattr(
        department_portal.Supervisor,
        "get",
        lambda *args, **kwargs: fake_supervisor,
    )

    response = client.post(
        "/members/update_eligibility",
        data={
            "supervisorID": "B00000001",
        },
    )

    assert response.status_code == 200
    assert fake_supervisor.isBanned is True
    fake_supervisor.save.assert_called_once()


@pytest.mark.integration
def test_update_eligibility_unbans_supervisor(
    client,
    monkeypatch,
):
    fake_supervisor = SimpleNamespace(
        ID="B00000001",
        isBanned=True,
        save=MagicMock(),
    )

    setCurrentUser(client, fakeAdminUser())

    monkeypatch.setattr(
        department_portal.Supervisor,
        "get",
        lambda *args, **kwargs: fake_supervisor,
    )

    response = client.post(
        "/members/update_eligibility",
        data={
            "supervisorID": "B00000001",
        },
    )

    assert response.status_code == 200
    assert fake_supervisor.isBanned is False
    fake_supervisor.save.assert_called_once()


@pytest.mark.integration
def test_update_eligibility_requires_permission(
    client,
    monkeypatch,
):
    setCurrentUser(client, fakeSupervisorUser())

    monkeypatch.setattr(
        department_portal,
        "render_template",
        lambda template: "Forbidden",
    )

    response = client.post(
        "/members/update_eligibility",
        data={
            "supervisorID": "B00000001",
        },
    )

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Forbidden"


# -------------------------------------------------------------------
# removeMember tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_remove_member(client, monkeypatch):
    fake_member = SimpleNamespace(
        delete_instance=MagicMock(),
    )

    setCurrentUser(client, fakeAdminUser())

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get",
        lambda *args, **kwargs: fake_member,
    )

    response = client.delete(
        "/members/remove",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
        },
    )

    assert response.status_code == 200
    fake_member.delete_instance.assert_called_once()


@pytest.mark.integration
def test_remove_member_requires_permission(client, monkeypatch):
    setCurrentUser(client, fakeSupervisorUser())

    monkeypatch.setattr(
        department_portal,
        "render_template",
        lambda template: "Forbidden",
    )

    response = client.delete(
        "/members/remove",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
        },
    )

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Forbidden"


# -------------------------------------------------------------------
# addUserToDept tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_add_existing_supervisor_to_department(
    client,
    monkeypatch,
):
    existing_supervisor = SimpleNamespace(
        ID="B00000001",
    )

    setCurrentUser(client, fakeAdminUser())

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get_or_none",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "get_or_none",
        lambda *args, **kwargs: existing_supervisor,
    )

    create_mock = MagicMock()

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "create",
        create_mock,
    )

    tracy_mock = MagicMock()

    monkeypatch.setattr(
        department_portal,
        "createSupervisorFromTracy",
        tracy_mock,
    )

    response = client.post(
        "/members/add",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
        },
    )

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "True"

    tracy_mock.assert_not_called()

    create_mock.assert_called_once_with(
        supervisor="B00000001",
        department="10",
    )


@pytest.mark.integration
def test_add_new_supervisor_to_department(
    client,
    monkeypatch,
):
    setCurrentUser(client, fakeAdminUser())

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get_or_none",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "get_or_none",
        lambda *args, **kwargs: None,
    )

    tracy_mock = MagicMock()
    create_mock = MagicMock()

    monkeypatch.setattr(
        department_portal,
        "createSupervisorFromTracy",
        tracy_mock,
    )

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "create",
        create_mock,
    )

    response = client.post(
        "/members/add",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
        },
    )

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "True"

    tracy_mock.assert_called_once_with(
        bnumber="B00000001"
    )

    create_mock.assert_called_once_with(
        supervisor="B00000001",
        department="10",
    )


@pytest.mark.integration
def test_add_user_rejects_duplicate_member(
    client,
    monkeypatch,
):
    existing_record = SimpleNamespace(
        supervisor="B00000001",
        department=10,
    )

    setCurrentUser(client, fakeAdminUser())

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get_or_none",
        lambda *args, **kwargs: existing_record,
    )

    create_mock = MagicMock()
    tracy_mock = MagicMock()

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "create",
        create_mock,
    )

    monkeypatch.setattr(
        department_portal,
        "createSupervisorFromTracy",
        tracy_mock,
    )

    response = client.post(
        "/members/add",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
        },
    )

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "False"

    create_mock.assert_not_called()
    tracy_mock.assert_not_called()


@pytest.mark.integration
def test_add_user_returns_500_when_creation_fails(
    client,
    monkeypatch,
):
    existing_supervisor = SimpleNamespace(
        ID="B00000001",
    )

    setCurrentUser(client, fakeAdminUser())

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get_or_none",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "get_or_none",
        lambda *args, **kwargs: existing_supervisor,
    )

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "create",
        MagicMock(
            side_effect=Exception("Database failed")
        ),
    )

    response = client.post(
        "/members/add",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
        },
    )

    assert response.status_code == 500


@pytest.mark.integration
def test_add_user_requires_permission(client, monkeypatch):
    setCurrentUser(client, fakeSupervisorUser())

    monkeypatch.setattr(
        department_portal,
        "render_template",
        lambda template: "Forbidden",
    )

    response = client.post(
        "/members/add",
        data={
            "supervisorID": "B00000001",
            "departmentID": "10",
        },
    )

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Forbidden"