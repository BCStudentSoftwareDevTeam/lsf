from app.models import *
from app.models.term import Term
from app.models.student import Student
from app.models.user import User
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.termPositionDescription import TermPositionDescription


# All caps fields are pulled from TRACY
class LaborStatusForm (baseModel):
    studentName                 = CharField(null=True)
    laborStatusFormID           = PrimaryKeyField()
    termCode                    = ForeignKeyField(Term, on_delete="cascade")             # FK to term
    studentSupervisee           = ForeignKeyField(Student, on_delete="cascade")          # foreign key to student
    supervisor                  = ForeignKeyField(Supervisor, on_delete="cascade")             # foreign key to supervisor
    department                  = ForeignKeyField(Department, on_delete="cascade")       # Foreign key to department
    termPositionDescription     = ForeignKeyField(TermPositionDescription, null=True, on_delete="cascade")
    jobType                     = CharField()                       # Primary or secondary
    WLS                         = CharField()
    POSN_TITLE                  = CharField()                       # eg. student programmer, customer engagement specialist, receptionist, teaching assistant
    POSN_CODE                   = CharField()
    positionDescription         = CharField(null=True)
    contractHours               = IntegerField(null=True)         # total hours for break terms
    weeklyHours                 = IntegerField(null=True)         # weekly hours 10,12,15...
    startDate                   = DateField(null=True)            # in case they start different than term start date
    endDate                     = DateField(null=True)
    supervisorNotes             = TextField(null=True)
    laborDepartmentNotes        = TextField(null=True)
    def __str__(self):
        return str(self.__dict__)
