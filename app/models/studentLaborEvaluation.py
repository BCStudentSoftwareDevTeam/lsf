from app.models import *
from app.models.formHistory import FormHistory

#Capitalized fields are originally from Tracy
class StudentLaborEvaluation(baseModel):
    ID                      = PrimaryKeyField()
    formHistoryID           = ForeignKeyField(FormHistory, on_delete="cascade")
    attendance_score        = IntegerField(null=False)
    attendance_comment      = TextField(null=False)
    accountability_score    = IntegerField(null=False)
    accountability_comment  = TextField(null=False)
    teamwork_score          = IntegerField(null=False)
    teamwork_comment        = TextField(null=False)
    initiative_score        = IntegerField(null=False)
    initiative_comment      = TextField(null=False)
    respect_score           = IntegerField(null=False)
    respect_comment         = TextField(null=False)
    learning_score          = IntegerField(null=False)
    learning_comment        = TextField(null=False)
    jobSpecific_score       = IntegerField(null=False)
    jobSpecific_comment     = TextField(null=False)
    transcript_comment      = TextField(null=True)
    is_midyear_evaluation   = BooleanField(default=False)
    is_submitted            = BooleanField(default=False)
    submitted_by            = CharField(null=False)

    def __str__(self):
        return str(self.__dict__)
