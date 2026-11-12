from flask import g
from app.models.term import *

def getCurrentAndNextAY():
    """
    Returns two Term peewee objects: one is the current academic year, 
    and the other is the next academic year (note that a new academic year
    begins from the start of July). 
    """

    currentYear, nextYear = g.currentAY

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