from app.models import *

#Capital attributes are originally pulled from TRACY
class Department(baseModel):
    departmentID            = PrimaryKeyField()
    DEPT_NAME               = CharField()
    ACCOUNT                 = CharField(null=True)
    ORG                     = CharField(null=True)
    departmentCompliance    = BooleanField(default=True)    # True if in compliance, false if out of it
    isActive                = BooleanField(default=True)
