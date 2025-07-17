from app.models import *
from app.models.student import Student
from app.models.supervisor import Supervisor
from peewee import CharField
# from app import login

from datetime import date
from app.models.department import Department
from peewee import CharField, fn



# Capitalized fields are originally pulled from tracy
class User(baseModel):
    userID              = PrimaryKeyField()
    student             = ForeignKeyField(Student, null=True)
    supervisor          = ForeignKeyField(Supervisor, null=True)
    username            = CharField(null=False)
    isLaborAdmin        = BooleanField(null=True)
    isFinancialAidAdmin = BooleanField(null=True)
    isSaasAdmin         = BooleanField(null=True)

    def __str__(self):
        return str(self.__dict__)
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self._ldsCache = None  

    # @property
    # def isLaborDepartmentStudent(self):
    #     if self._ldsCache is None:
    #         if not self.student:
    #             self._ldsCache = False
    #         else:
    #             from app.models.laborStatusForm import LaborStatusForm
    #             from app.models.formHistory import FormHistory
    #             from app.models.status import Status
    #             today = date.today()

    #             # Get the approved status record
    #             try:
    #                 approved_status = Status.get(Status.statusName == "Approved")
    #             except Status.DoesNotExist:
    #                 # If no approved status exists, no forms can be approved
    #                 self._ldsCache = False
    #                 return self._ldsCache
                

    #             # Subquery to check if student has an approved release form
    #             released_forms = (
    #                 FormHistory
    #                 .select(FormHistory.formID)
    #                 .where(
    #                     (FormHistory.releaseForm.is_null(False)) &  # Has a release form
    #                     (FormHistory.status == approved_status)     # Release form is approved
    #                 )
    #             )

    #             labor_status_forms = (
    #                 LaborStatusForm
    #                 .select()
    #                 .join(Department, on=(LaborStatusForm.department == Department.departmentID))
    #                 .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
    #                 .where(
    #                     (LaborStatusForm.studentSupervisee == self.student) &
    #                     (LaborStatusForm.startDate <= today) &
    #                     (LaborStatusForm.endDate >= today) &
    #                     (Department.isActive == True) &
    #                     (fn.BINARY(Department.DEPT_NAME) == "Labor Department") & # comparison case sensetive.
    #                     (FormHistory.status == approved_status) & # Ensure form is approved
    #                     ~(LaborStatusForm.laborStatusFormID.in_(released_forms))  # Exclude released students
    #                 )
    #             )
            
    #             self._ldsCache = labor_status_forms.exists()
    #             return self._ldsCache
        
    @property
    def isLaborDepartmentStudent(self):
        if self._ldsCache is not None:  
            return self._ldsCache
            
        if not self.student:
            self._ldsCache = False
            return self._ldsCache

        from app.models.laborStatusForm import LaborStatusForm
        from app.models.formHistory import FormHistory
        from app.models.status import Status
        today = date.today()

        # Get the approved status record
        try:
            approved_status = Status.get(Status.statusName == "Approved")
        except Status.DoesNotExist:
            # If no approved status exists, no forms can be approved
            self._ldsCache = False
            return self._ldsCache

        # Subquery to check if student has an approved release form
        released_forms = (
            FormHistory
            .select(FormHistory.formID)
            .where(
                (FormHistory.releaseForm.is_null(False)) &  # Has a release form
                (FormHistory.status == approved_status)     # Release form is approved
            )
        )

        labor_status_forms = (
            LaborStatusForm
            .select()
            .join(Department, on=(LaborStatusForm.department == Department.departmentID))
            .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
            .where(
                (LaborStatusForm.studentSupervisee == self.student) &
                (LaborStatusForm.startDate <= today) &
                (LaborStatusForm.endDate >= today) &
                (Department.isActive == True) &
                (fn.BINARY(Department.DEPT_NAME) == "Labor Department") & 
                (FormHistory.status == approved_status) &  
                ~(LaborStatusForm.laborStatusFormID.in_(released_forms))  # Exclude released students
            )
        )

        self._ldsCache = labor_status_forms.exists()
        return self._ldsCache   

    @property
    def firstName(self):
        if self.supervisor:
            return self.supervisor.FIRST_NAME
        elif self.student:
            return self.student.FIRST_NAME

        return ""

    @property
    def lastName(self):
        if self.supervisor:
            return self.supervisor.LAST_NAME
        elif self.student:
            return self.student.LAST_NAME

        return ""

    @property
    def fullName(self):
        return self.firstName + " " + self.lastName

    @property
    def email(self):
        if self.supervisor:
            return self.supervisor.EMAIL
        elif self.student:
            return self.student.STU_EMAIL

        return ""

