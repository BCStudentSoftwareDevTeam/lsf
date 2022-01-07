from app.models import *
from app.models.formHistory import FormHistory

#Capitalized fields are originally from Tracy
class StudentLaborEvaluation(baseModel):
    ID                      = PrimaryKeyField()
    formHistoryID           = ForeignKeyField(FormHistory, on_delete="cascade")
    attendance_score        = IntegerField(null=False)
    attendance_comment      = CharField(null=False)
    accountability_score    = IntegerField(null=False)
    accountability_comment  = CharField(null=False)
    teamwork_score          = IntegerField(null=False)
    teamwork_comment        = CharField(null=False)
    initiative_score        = IntegerField(null=False)
    initiative_comment      = CharField(null=False)
    respect_score           = IntegerField(null=False)
    respect_comment         = CharField(null=False)
    learning_score          = IntegerField(null=False)
    learning_comment        = CharField(null=False)
    jobSpecific_score       = IntegerField(null=False)
    jobSpecific_comment     = CharField(null=False)

    def __str__(self):
        return str(self.__dict__)
