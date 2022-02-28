from app.models import *


class Term(baseModel):
    termCode                = IntegerField(primary_key=True)                        # Term codes, like 201612 for Spring 2017. Matches Banner nomenclature Need to make new for AY.
    termName                = CharField(null=False)                                 # Spring 2020 only, Summer, Chsirtmas Break, AY 2020-2021
    termStart               = DateField(null=True, default=None)                    # start date
    termEnd                 = DateField(null=True, default=None)                    # end date
    primaryCutOff           = DateField(null=True, default=None)                    # Cut off date for primary position submission
    adjustmentCutOff        = DateField(null=True, default=None)                    # Cut off date for the adjustment of labor status forms
    termState               = BooleanField(default=False)                           #open, closed, inactive
    isBreak                 = BooleanField(default=False)
    isSummer                = BooleanField(default=False)
    isAcademicYear          = BooleanField(default=False)
    isFinalEvaluationOpen   = BooleanField(default=False)
    isMidyearEvaluationOpen = BooleanField(default=False)
