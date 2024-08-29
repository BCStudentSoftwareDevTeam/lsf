from app.controllers.api_routes.apiClasses import LaborFormsForDepartmentApi, LaborFormsForStudentApi

def initializeApiRoutes(api):
    api.add_resource(LaborFormsForDepartmentApi, '/api/org/<orgCode>')
    api.add_resource(LaborFormsForStudentApi, '/api/usr/<bNumber>')
