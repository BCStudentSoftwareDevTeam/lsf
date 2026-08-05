from flask import g
from app.models.term import *

def getCurrentAndNextAY():
    """
    Returns two Term peewee objects: one is the current academic year, 
    and the other is the next academic year.
    """

    currentYear      = g.openTerm.termCode // 100
    nextYear         = currentYear + 1

    currentAYCode    = currentYear * 100
    nextAYCode       = nextYear * 100

    currentAY, _  = Term.get_or_create(
        termCode=currentAYCode,
        defaults={"termName": "AY {}-{}".format(currentYear, currentYear + 1), "isAcademicYear": True}
        )
    
    nextAY, _     = Term.get_or_create(
        termCode=nextAYCode,
        defaults={"termName": "AY {}-{}".format(nextYear, nextYear + 1), "isAcademicYear": True}
    )

    return (currentAY, nextAY)