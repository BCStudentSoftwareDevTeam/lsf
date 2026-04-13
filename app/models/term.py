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
        Accepts the results of a query where each object has a `termCode` attribute.
        To collapse selected columns from other tables into an objects direct attributes
        use the .objects() method on the query. See peewee documentation for more details.

        Sorts by the Term Code in logical order based first on year and then by the seasonalCode
        
        seasonalCode := last two digits of the term code which maps arbitrarily to the name of the term, break, etc.
        """
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

        # Sort by seasonal code
        result = sorted(queryResult, key=lambda e: seasonalCodeToOrderValue[str(e.termCode)[4:]], reverse=reverse)
        # Sort by year
        return sorted(result, key=lambda e: str(e.termCode)[:4], reverse=reverse)
