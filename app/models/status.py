from app.models import *

# Approved, denied by student, denied by admin, pending, pre-student approval
class Status(baseModel):
    statusName         = CharField(primary_key=True) 
