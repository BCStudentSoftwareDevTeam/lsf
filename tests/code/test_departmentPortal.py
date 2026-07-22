import pytest

from types import SimpleNamespace
from unittest.mock import MagicMock
from flask import Flask

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
    )

    test_app.register_blueprint(department_portal.main_bp)

    return test_app


@pytest.fixture
def client(app):
    """
    Creates a Flask test client.
    """
    return app.test_client()


# -------------------------------------------------------------------
# manageMembers tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_manage_members_for_supervisor(client, monkeypatch):
    fake_user = SimpleNamespace(
        supervisor="B00000001",
        student=None,
        isLaborAdmin=False,
    )

    fake_supervisor = SimpleNamespace(
        ID="B00000001",
        legal_name="Test Supervisor",
    )

    fake_department = SimpleNamespace(
        departmentID=10,
        ORG=2114,
        ACCOUNT="60000",
        DEPT_NAME="Computer Science",
    )

    fake_members = [
        {
            "supervisor": "B00000002",
            "LAST_NAME": "Scott",
        }
    ]

    fake_counts = {
        "B00000002": 3,
    }

    fake_members_with_counts = [
        {
            "supervisor": "B00000002",
            "LAST_NAME": "Scott",
            "positionCount": 3,
        }
    ]

    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: fake_user,
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "get",
        lambda *args, **kwargs: fake_supervisor,
    )

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
        currentSupervisor=fake_supervisor,
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
    )

    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: fake_user,
    )

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


@pytest.mark.integration
def test_manage_members_returns_403_for_unauthorized_user(
    client,
    monkeypatch,
):
    fake_user = SimpleNamespace(
        supervisor=None,
        student=None,
        isLaborAdmin=False,
    )

    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: fake_user,
    )

    monkeypatch.setattr(
        department_portal,
        "render_template",
        lambda template: "Forbidden",
    )

    response = client.get(
        "/department/2114/60000/members"
    )

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Forbidden"


@pytest.mark.integration
def test_manage_members_returns_403_when_user_is_none(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: None,
    )

    monkeypatch.setattr(
        department_portal,
        "render_template",
        lambda template: "Forbidden",
    )

    response = client.get(
        "/department/2114/60000/members"
    )

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Forbidden"


# -------------------------------------------------------------------
# searchMember tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_search_member_by_bnumber(client, monkeypatch):
    fake_user = SimpleNamespace(
        supervisor="B00000001",
        student=None,
        isLaborAdmin=False,
    )

    fake_database_supervisor = SimpleNamespace(
        ID="B00000002",
    )

    fake_query = MagicMock()
    fake_query.where.return_value = [
        fake_database_supervisor,
    ]

    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: fake_user,
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "select",
        lambda: fake_query,
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


@pytest.mark.integration
def test_search_member_by_single_name(client, monkeypatch):
    fake_user = SimpleNamespace(
        supervisor="B00000001",
        student=None,
        isLaborAdmin=False,
    )

    fake_database_supervisor = SimpleNamespace(
        ID="B00000003",
    )

    fake_query = MagicMock()
    fake_query.where.return_value = [
        fake_database_supervisor,
    ]

    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: fake_user,
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "select",
        lambda: fake_query,
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


@pytest.mark.integration
def test_search_member_by_full_name(client, monkeypatch):
    fake_user = SimpleNamespace(
        supervisor="B00000001",
        student=None,
        isLaborAdmin=False,
    )

    fake_database_supervisor = SimpleNamespace(
        ID="B00000004",
    )

    fake_query = MagicMock()
    fake_query.where.return_value = [
        fake_database_supervisor,
    ]

    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: fake_user,
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "select",
        lambda: fake_query,
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


@pytest.mark.integration
def test_search_member_removes_duplicates(client, monkeypatch):
    fake_user = SimpleNamespace(
        supervisor="B00000001",
        student=None,
        isLaborAdmin=False,
    )

    duplicate_supervisor_one = SimpleNamespace(
        ID="B00000002",
    )

    duplicate_supervisor_two = SimpleNamespace(
        ID="B00000002",
    )

    fake_query = MagicMock()
    fake_query.where.return_value = [
        duplicate_supervisor_one,
        duplicate_supervisor_two,
    ]

    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: fake_user,
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "select",
        lambda: fake_query,
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
    assert len(response.get_json()) == 1


@pytest.mark.integration
def test_search_member_returns_403_for_unauthorized_user(
    client,
    monkeypatch,
):
    fake_user = SimpleNamespace(
        supervisor=None,
        student=None,
        isLaborAdmin=False,
    )

    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: fake_user,
    )

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


@pytest.mark.integration
def test_search_member_allows_labor_admin(
    client,
    monkeypatch,
):
    fake_user = SimpleNamespace(
        supervisor=None,
        student=None,
        isLaborAdmin=True,
    )

    fake_query = MagicMock()
    fake_query.where.return_value = []

    monkeypatch.setattr(
        department_portal,
        "require_login",
        lambda: fake_user,
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "select",
        lambda: fake_query,
    )

    response = client.get(
        "/members/search/Unknown"
    )

    assert response.status_code == 200
    assert response.get_json() == []


# -------------------------------------------------------------------
# coordinatorSwitch tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_coordinator_switch_assigns_coordinator(
    client,
    monkeypatch,
):
    fake_member = SimpleNamespace(
        isCoordinator=False,
        save=MagicMock(),
    )

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get",
        lambda *args, **kwargs: fake_member,
    )

    with client.session_transaction() as test_session:
        test_session["current_department_id"] = 10

    response = client.post(
        "/members/coordinator_switch",
        json={
            "supervisorID": "B00000001",
            "isCoordinator": True,
        },
    )

    assert response.status_code == 200
    assert fake_member.isCoordinator is True
    fake_member.save.assert_called_once()


@pytest.mark.integration
def test_coordinator_switch_removes_coordinator(
    client,
    monkeypatch,
):
    fake_member = SimpleNamespace(
        isCoordinator=True,
        save=MagicMock(),
    )

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get",
        lambda *args, **kwargs: fake_member,
    )

    with client.session_transaction() as test_session:
        test_session["current_department_id"] = 10

    response = client.post(
        "/members/coordinator_switch",
        json={
            "supervisorID": "B00000001",
            "isCoordinator": False,
        },
    )

    assert response.status_code == 200
    assert fake_member.isCoordinator is False
    fake_member.save.assert_called_once()


@pytest.mark.integration
def test_coordinator_switch_requires_department_session(
    client,
):
    response = client.post(
        "/members/coordinator_switch",
        json={
            "supervisorID": "B00000001",
            "isCoordinator": True,
        },
    )

    assert response.status_code == 400


# -------------------------------------------------------------------
# eligibility switch tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_eligibility_switch_bans_supervisor(
    client,
    monkeypatch,
):
    fake_supervisor = SimpleNamespace(
        ID="B00000001",
        isBanned=False,
        save=MagicMock(),
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "get",
        lambda *args, **kwargs: fake_supervisor,
    )

    response = client.post(
        "/members/ban_switch",
        json={
            "supervisorID": "B00000001",
        },
    )

    assert response.status_code == 200
    assert fake_supervisor.isBanned is True
    fake_supervisor.save.assert_called_once()


@pytest.mark.integration
def test_eligibility_switch_unbans_supervisor(
    client,
    monkeypatch,
):
    fake_supervisor = SimpleNamespace(
        ID="B00000001",
        isBanned=True,
        save=MagicMock(),
    )

    monkeypatch.setattr(
        department_portal.Supervisor,
        "get",
        lambda *args, **kwargs: fake_supervisor,
    )

    response = client.post(
        "/members/ban_switch",
        json={
            "supervisorID": "B00000001",
        },
    )

    assert response.status_code == 200
    assert fake_supervisor.isBanned is False
    fake_supervisor.save.assert_called_once()


# -------------------------------------------------------------------
# removeMember tests
# -------------------------------------------------------------------


@pytest.mark.integration
def test_remove_member(client, monkeypatch):
    fake_member = SimpleNamespace(
        delete_instance=MagicMock(),
    )

    monkeypatch.setattr(
        department_portal.SupervisorDepartment,
        "get",
        lambda *args, **kwargs: fake_member,
    )

    with client.session_transaction() as test_session:
        test_session["current_department_id"] = 10

    response = client.delete(
        "/members/remove",
        json={
            "supervisorID": "B00000001",
        },
    )

    assert response.status_code == 200
    fake_member.delete_instance.assert_called_once()


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