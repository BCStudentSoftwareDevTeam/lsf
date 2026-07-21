import re
from datetime import date
from flask import render_template, request, json, redirect, session, url_for, send_file, g, flash, jsonify
from peewee import JOIN, DoesNotExist, fn, Case
from functools import reduce
import operator
from app.logic.userInsertFunctions import createSupervisorFromTracy
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.term import Term
from app.controllers.admin_routes.allPendingForms import checkAdjustment
from app.controllers.main_routes import main_bp
from app.logic.download import CSVMaker, saveFormSearchResult, retrieveFormSearchResult
from app.logic.search import getDepartmentsForSupervisor, searchPerson, searchSupervisorPortal
from app.login_manager import require_login, logout
from app.logic.getTableData import getDatatableData
from app.logic.banner import Banner
from flask import abort
from app.logic.search import limitSearchByUserDepartment, studentDbToDict, usernameFromEmail

def supervisorsDbToDict(supervisor):
    """
    Given a supervisor object it will return a mapped Dict with supervisor data.
    """
    dbToDict =  {'username': usernameFromEmail(supervisor.EMAIL.strip()),
                'firstName': supervisor.FIRST_NAME.strip(),
                'lastName': supervisor.LAST_NAME.strip(),
                'bnumber': supervisor.ID.strip(),
                'department': supervisor.DEPT_NAME.strip(),
                'type': 'Supervisor'}
    return dbToDict

def currentAcademicYear():
    """
    Finds the current academic year
    """
    today = date.today()
    currentYear = today.year
    if today.month < 7: 
        currentAcademicYear = (currentYear - 1, currentYear)
    else: 
        currentAcademicYear = (currentYear, currentYear + 1)
    # Note that the start of July is 
    # normally considered the start of a new academic year.

    return currentAcademicYear

def getCurrentDepartment(org, account):
    """Look up the department by org/account, stash it in session, or 404."""
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        abort(404)
    session['current_department_id'] = dept.departmentID
    session['current_department'] = dept.DEPT_NAME
    return dept


def getDepartmentMembers(dept):
    """Supervisor-department rows for a department, as dicts."""
    return list(
        SupervisorDepartment.select(SupervisorDepartment, Supervisor)
        .where(SupervisorDepartment.department == dept)
        .join(Supervisor)
        .dicts()
    )


def getReleasedFormIds():
    """formIDs for labor release forms already in effect as of today."""
    today = date.today()
    return (
        FormHistory.select(FormHistory.formID)
        .join(LaborReleaseForm)
        .where(
            (FormHistory.historyType == "Labor Release Form") &
            (FormHistory.status == "Approved") &
            (LaborReleaseForm.releaseDate <= today)
        )
    )


def getStudentCounts(dept):
    """Active/pending primary/secondary position counts, keyed by (dept, supervisor)."""
    releasedForms = getReleasedFormIds()

    activePrimaries = (LaborStatusForm.jobType == 'Primary') & (LaborStatusForm.studentConfirmation == True)
    pendingPrimaries = (LaborStatusForm.jobType == 'Primary') & (LaborStatusForm.studentConfirmation.is_null(True))
    activeSecondaries = (LaborStatusForm.jobType == 'Secondary') & (LaborStatusForm.studentConfirmation == True)
    pendingSecondaries = (LaborStatusForm.jobType == 'Secondary') & (LaborStatusForm.studentConfirmation.is_null(True))

    rows = list(
        LaborStatusForm.select(
            fn.SUM(Case(None, ((activePrimaries, 1),), 0)).alias("active_primary_positions"),
            fn.SUM(Case(None, ((pendingPrimaries, 1),), 0)).alias("pending_primary_positions"),
            fn.SUM(Case(None, ((activeSecondaries, 1),), 0)).alias("active_secondary_positions"),
            fn.SUM(Case(None, ((pendingSecondaries, 1),), 0)).alias("pending_secondary_positions"),
            LaborStatusForm.department,
            LaborStatusForm.supervisor
        ).where(
            (LaborStatusForm.department == dept) &
            (LaborStatusForm.laborStatusFormID.not_in(releasedForms))
        ).group_by(
            LaborStatusForm.department, LaborStatusForm.supervisor
        ).dicts()
    )
    return {(row["department"], row["supervisor"]): row for row in rows}


def attachPositionCounts(members, counts):
    """Merge counts onto each member dict, defaulting missing values to 0."""
    fields = [
        "active_primary_positions", "pending_primary_positions",
        "active_secondary_positions", "pending_secondary_positions",
    ]
    for member in members:
        row = counts.get((member["department"], member["supervisor"]), {})
        for field in fields:
            member[field] = row.get(field, 0)

    return members


