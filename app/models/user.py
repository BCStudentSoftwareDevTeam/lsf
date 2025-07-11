from app.models import *
from app.models.student import Student
from app.models.supervisor import Supervisor
from peewee import CharField
# from app import login

from datetime import date
from app.models.department import Department


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
    
    # def __init__(self,*args, **kwargs):
    #     super().__init__(*args,**kwargs)
    #     self._ldsCache = None
    
    @property
    def isLaborDepartmentStudent(self):
        if self._ldsCache is None:
            return self._ldsCache
       
        if not self.student:
            self._ldsCache = False
            return False
        
        from app.models.laborStatusForm import LaborStatusForm
        today = date.today()

        labor_status_forms = (
            LaborStatusForm
            .select()
            .join(Department, on=(LaborStatusForm.department == Department.departmentID))
            .where(
                (LaborStatusForm.studentSupervisee == self.student) &
                (LaborStatusForm.startDate <= today) &
                (LaborStatusForm.endDate >= today) &
                (Department.isActive == True) &
                (fn.BINARY(Department.DEPT_NAME) == "Labor Department") # comparison case sensetive.
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

