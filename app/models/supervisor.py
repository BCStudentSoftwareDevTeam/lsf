from app.models import *
from peewee import CharField
# from app import login


# Capitalized fields are originally pulled from tracy
class Supervisor(baseModel):
    ID                  = CharField(primary_key=True)  #B-number
    PIDM                = IntegerField(null=True)  # from Tracy
    LAST_NAME           = CharField(null=True)
    EMAIL               = CharField(null=True)
    CPO                 = CharField(null=True)
    ORG                 = CharField(null=True)
    DEPT_NAME           = CharField(null=True)

    legal_name      = CharField(null=True)
    preferred_name  = CharField(null=True)

    @property
    def FIRST_NAME(self):
        return self.preferred_name or self.legal_name
