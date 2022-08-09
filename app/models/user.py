from app.models import *
from app.models.student import Student
from app.models.supervisor import Supervisor
from peewee import CharField
# from app import login


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

