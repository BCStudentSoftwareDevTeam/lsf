from app.models import *
from collections import defaultdict


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


    @staticmethod
    def order_by_term(queryResult, *, reverse=False):
        """
        Accepts the results of a query where each object has had a `termCode` column selected.
        Sorts by the Term Code in logical order based first on year and then by the seasonalCode
        
        seasonalCode := last two digits of the term code which maps arbitrarily to the name of the term, break, etc.
        """
        print(dir(queryResult[0])) # beans
        print("*"*100)
        seasonalCodeToOrderValue = defaultdict(lambda: 1)
        seasonalCodeToOrderValue.update({
            '00' : 0,
            '11' : 2,
            '04' : 3,
            '01' : 4,
            '02' : 5,
            '12' : 6,
            '05' : 7,
            '03' : 8,
            '13' : 9,
        })
        # TODO: beans, We'd like to use simply e.termCode here but for some reason we cannot select for it.
        # To solve the immediate problem, we're trying to use a peewee object way of looking at it by going through
        # .formID first but we're getting another error about departments now. We should try to comment out the line
        # that calls this function to order them at all to ensure that the problem is what we're doing here.

        # Sort by seasonal code
        result = sorted(queryResult, key=lambda e: seasonalCodeToOrderValue[str(e.formID.termCode)[4:]], reverse=reverse)
        # Sort by year
        return sorted(result, key=lambda e: str(e.formID.termCode)[:4], reverse=reverse)
