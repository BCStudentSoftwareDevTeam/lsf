from flask import (
    current_app,
    g,
    jsonify,
    render_template,
    request,
)

from app.models.department import Department
from app.models.supervisorDepartment import SupervisorDepartment
from app.logic.boxPositionManager import BoxPositionImporter
from app.controllers.admin_routes import admin
from datetime import date

def getImportDepartments(currentUser):
    query = Department.select()

    if not currentUser.isLaborAdmin:
        query = (
            query
            .join(SupervisorDepartment)
            .where(
                SupervisorDepartment.supervisor
                == currentUser.supervisor
            )
            .distinct()
        )

    return list(
        query.order_by(
            Department.isActive.desc(),
            Department.DEPT_NAME.asc(),
        )
    )


@admin.route("/positions/import", methods=["GET"])
def positionImportPage():
    departments = getImportDepartments(g.currentUser)

    return render_template(
        "admin/positionimport.html",
        departments=departments,
    )


@admin.route("/positions/import", methods=["POST"])
def importPositions():
    currentUser = g.currentUser
    departments = getImportDepartments(currentUser)

    allowedDepartmentIDs = {
        department.departmentID
        for department in departments
    }

    if not allowedDepartmentIDs:
        return jsonify(
            error="No departments are available for import."
        ), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            error="Expected a JSON object."
        ), 400

    credentials = {}

    credentialFields = {
        "boxClientID": "Box Client ID",
        "boxClientSecret": "Box Client Secret",
        "boxAccessToken": "Box Access Token",
        "boxFolderID": "Box Folder ID",
    }

    for field, label in credentialFields.items():
        value = data.get(field)

        if not isinstance(value, str) or not value.strip():
            return jsonify(
                error=f"{label} is required."
            ), 400

        credentials[field] = value.strip()

    if not credentials["boxFolderID"].isdigit():
        return jsonify(
            error="Box Folder ID must be numeric."
        ), 400

    def optionalInteger(field):
        value = data.get(field)

        if value is None or value == "":
            return None

        if isinstance(value, bool) or not isinstance(value, (str, int)):
            raise ValueError(f"{field} must be an integer.")

        return int(value)

    def optionalDate(field):
        value = data.get(field)

        if value is None or value == "":
            return None

        if not isinstance(value, str):
            raise ValueError(f"{field} must be a date.")

        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError(
                f"{field} must be a valid date in YYYY-MM-DD format."
            )

    try:
        departmentID = optionalInteger("departmentID")
        wls = optionalInteger("wls")
        revisionStart = optionalDate("revisionStart")
        revisionEnd = optionalDate("revisionEnd")

        if wls is not None and wls not in range(1, 8):
            raise ValueError("WLS must be 1–6 or Special.")

        if (
            revisionStart is not None
            and revisionEnd is not None
            and revisionStart > revisionEnd
        ):
            raise ValueError(
                "The start date must be on or before the end date."
            )

    except (TypeError, ValueError) as error:
        return jsonify(error=str(error)), 400

    if (
        departmentID is not None
        and departmentID not in allowedDepartmentIDs
    ):
        return jsonify(
            error="You do not have access to that department."
        ), 403

    try:
        manager = BoxPositionImporter(
            clientID=credentials["boxClientID"],
            clientSecret=credentials["boxClientSecret"],
            accessToken=credentials["boxAccessToken"],
            folderID=credentials["boxFolderID"],
        )

        summary = manager.migrateDocument(
            departmentID=departmentID,
            wls=wls,
            revisionStart=revisionStart,
            revisionEnd=revisionEnd,
            revisedBy="Box import",
            status="Active",
            allowedDepartmentIDs=allowedDepartmentIDs,
        )

        # Do not return raw SDK errors, which may contain credentials.
        return jsonify(
            imported=summary["imported"],
            existing=summary["existing"],
            filtered=summary["filtered"],
            failed=summary["failed"],
            errors=[
                {
                    "file": error["file"],
                    "message": (
                        "Could not import this document. "
                        "Check its format and department information."
                    ),
                }
                for error in summary.get("errors", [])
            ],
        )

    except Exception as error:
        # Log only the exception type, not credentials or request data.
        current_app.logger.error(
            "Box position import failed (%s)",
            type(error).__name__,
        )

        return jsonify(
            error=(
                "The import could not finish. Check your Box credentials, "
                "folder ID, and access permissions. Some documents may "
                "already have been imported; existing revisions will be "
                "skipped when you retry."
            )
        ), 500