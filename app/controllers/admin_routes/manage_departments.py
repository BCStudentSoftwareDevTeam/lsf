import io
import xlsxwriter
from flask import send_file
from app.controllers.admin_routes import *
from app.models.user import *
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.allocation import Allocation
from app.models.department import Department
from app.login_manager import require_login
from app.logic.search import getSupervisorsForDepartment
from app.controllers.admin_routes import admin
from app.controllers.errors_routes.handlers import *
#from app.models.manageDepartments import *
from app.models.term import *
from flask_bootstrap import bootstrap_find_resource
from app.models.department import *
from flask import request, redirect
from flask import jsonify
from playhouse.shortcuts import model_to_dict
from app.logic.tracy import Tracy

@admin.route('/admin/manageDepartments', methods=['GET'])
# @login_required
def manage_departments():
    """
    Updates the Labor Status Forms database with any new departments in the Tracy database on page load.
    Returns the departments to be used in the HTML for the manage departments page.
    """
    try:
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html')
        if not currentUser.isLaborAdmin:       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor:
                return render_template('errors/403.html'), 403


        activeDepartments = Department.select().where(Department.isActive == True)
        inactiveDepartments = Department.select().where(Department.isActive == False)
        allSupervisors= Supervisor.select().order_by(Supervisor.LAST_NAME)
        academicYears = (
            Term.select()
            .join(Allocation, on=(Term.termCode == Allocation.termCode))
            .where(
                ((Term.isAcademicYear == True) | Term.termName.startswith("AY ")) &
                (Allocation.isFinal == True)
            )
            .distinct()
            .order_by(Term.termCode.desc())
        )
        return render_template( 'admin/manageDepartments.html',
                                title = ("Manage Departments"),
                                activeDepartments = activeDepartments,
                                inactiveDepartments = inactiveDepartments,
                                allSupervisors = allSupervisors,
                                academicYears = academicYears
                                )
    except Exception as e:
        print("Error Loading all Departments", e)
        return render_template('errors/500.html'), 500


def _get_final_allocations_for_year(academicYearCode):
    academicYear = Term.get_or_none(
        (Term.termCode == academicYearCode) &
        ((Term.isAcademicYear == True) | Term.termName.startswith("AY "))
    )
    if not academicYear:
        return None, []

    allocations = list(
        Allocation.select(Allocation, Department)
        .join(Department)
        .where(
            (Allocation.termCode == academicYearCode) &
            (Allocation.isFinal == True)
        )
        .order_by(Department.DEPT_NAME)
    )
    return academicYear, allocations


def _allocation_preview_record(allocation):
    return {
        "department": allocation.department.DEPT_NAME,
        "primary_10": allocation.primary_10,
        "primary_12": allocation.primary_12,
        "primary_15": allocation.primary_15,
        "primary_20": allocation.primary_20,
        "secondary_5": allocation.secondary_5,
        "secondary_10": allocation.secondary_10,
        "break_hours": allocation.breakHours,
    }


@admin.route('/admin/manageDepartments/allocations/<int:academicYearCode>', methods=['GET'])
def previewAllocationDownload(academicYearCode):
    currentUser = require_login()
    if not currentUser or not currentUser.isLaborAdmin:
        return jsonify({"error": "Labor administrator access is required."}), 403

    academicYear, allocations = _get_final_allocations_for_year(academicYearCode)
    if not academicYear or not allocations:
        return jsonify({"error": "No final allocations were found for that academic year."}), 404

    return jsonify({
        "academicYear": academicYear.termName,
        "allocations": [_allocation_preview_record(allocation) for allocation in allocations],
    })


@admin.route('/admin/manageDepartments/allocations/download/<int:academicYearCode>', methods=['GET'])
def downloadAllocations(academicYearCode):
    currentUser = require_login()
    if not currentUser or not currentUser.isLaborAdmin:
        return render_template('errors/403.html'), 403

    academicYear, allocations = _get_final_allocations_for_year(academicYearCode)
    if not academicYear or not allocations:
        return render_template('errors/404.html'), 404

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Allocations")
    headers = [
        "Department", "Academic Year", "Primary 10", "Primary 12", "Primary 15",
        "Primary 20", "Secondary 5", "Secondary 10", "Break Hours",
        "Total Primaries", "Total Secondaries", "Total Allocations",
        "Approved On", "Approved By ID", "Justification",
    ]
    headerFormat = workbook.add_format({"bold": True, "bg_color": "#D9EAF7"})
    for column, header in enumerate(headers):
        worksheet.write_string(0, column, header, headerFormat)

    for rowIndex, allocation in enumerate(allocations, start=1):
        primaryTotal = allocation.primary_10 + allocation.primary_12 + allocation.primary_15 + allocation.primary_20
        secondaryTotal = allocation.secondary_5 + allocation.secondary_10
        values = [
            allocation.department.DEPT_NAME,
            academicYear.termName,
            allocation.primary_10,
            allocation.primary_12,
            allocation.primary_15,
            allocation.primary_20,
            allocation.secondary_5,
            allocation.secondary_10,
            allocation.breakHours,
            primaryTotal,
            secondaryTotal,
            primaryTotal + secondaryTotal,
            allocation.approvedOn.isoformat() if allocation.approvedOn else "",
            allocation.approvedBy_id or "",
            allocation.justification or "",
        ]
        for column, value in enumerate(values):
            if isinstance(value, int):
                worksheet.write_number(rowIndex, column, value)
            else:
                worksheet.write_string(rowIndex, column, str(value))

    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(0, 0, len(allocations), len(headers) - 1)
    worksheet.set_column(0, 1, 24)
    worksheet.set_column(2, 13, 16)
    worksheet.set_column(14, 14, 48)
    workbook.close()
    output.seek(0)

    filename = f"allocations_{academicYearCode}.xlsx"
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )


@admin.route("/admin/manageDepartments/<departmentID>", methods=['GET'])
def getSupervisorsInDepartment(departmentID):
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html')
        if not currentUser.isLaborAdmin:       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor:
                return render_template('errors/403.html'), 403
        
        supervisors = getSupervisorsForDepartment(departmentID)
        supervisors = [model_to_dict(supervisor) for supervisor in supervisors]
        return jsonify(supervisors)
    
@admin.route('/admin/manageDepartments/removeSupervisorFromDepartment', methods=['POST'])
def removeSupervisorFromDepartment():
    try:
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html')
        if not currentUser.isLaborAdmin:       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor:
                return render_template('errors/403.html'), 403
        
        formData = request.form
        supervisorDeptRecord = SupervisorDepartment.get_or_none(supervisor = formData['supervisorID'], department = formData['departmentID'])
    
        if supervisorDeptRecord:
            supervisorDeptRecord.delete_instance()
            return "True"
        else:
            return "False"
    
    except Exception as e:
        print(f'Could not remove user from department: {e}')
        return "", 500

@admin.route('/admin/complianceStatus', methods=['POST'])
def complianceStatusCheck():
    """
    This function changes the compliance status in the database for labor status forms.  It works in collaboration with the ajax call in manageDepartments.js
    """
    try:
        rsp = eval(request.data.decode("utf-8")) # This fixes byte indices must be intergers or slices error
        if rsp:
            department = Department.get(int(rsp['deptName']))
            department.departmentCompliance = not department.departmentCompliance
            department.save()
            return jsonify({"Success": True})
    except Exception as e:
        print(e)
        return jsonify({"Success": False})
