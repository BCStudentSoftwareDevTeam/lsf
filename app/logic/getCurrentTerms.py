from app.models.term import Term
from datetime import datetime, date

def getCurrentTerms():
    '''
    Gets 3 primary terms for the current Academic Year (AY)
    This means it attempt to get an AY, fall term, and spring term
    This returns all three objects individually for each of the terms.
    '''
    currentDate = date.today()
    if currentDate.month <= 6:
        # If it is the spring semester, then the term code is 1 year behind. e.g. 2025-2026 term code is 202500. Thus the - 100 in the spring term.
        # The (year * 100) turns the year into an AY term code, 2025 -> 202500. The + 12/11 turns it into a fall or spring term.
        springTerm = Term.select().where(Term.termCode == currentDate.year * 100 + 12 - 100).get()
        currentAY = Term.select().where(Term.termCode == currentDate.year * 100 - 100).get()
        fallTerm = Term.select().where(Term.termCode == currentDate.year * 100 + 11 - 100).get()
        return currentAY, fallTerm, springTerm

    else:
        fallTerm = Term.select().where(Term.termCode == currentDate.year * 100 + 11).get()
        currentAY = Term.select().where(Term.termCode == currentDate.year * 100).get()
        springTerm = Term.select().where(Term.termCode == currentDate.year * 100 + 12).get()
        return currentAY, fallTerm, springTerm

