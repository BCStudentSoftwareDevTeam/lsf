from flask import jsonify
from app.config.loadConfig import*
from app import app

from app.models.laborStatusForm import LaborStatusForm

def getCeltsLaborPosition():
    celtsLabor = (LaborStatusForm.select(LaborStatusForm.studentName, LaborStatusForm.termCode_id, LaborStatusForm.POSN_TITLE, LaborStatusForm.POSN_CODE)
                                 .where(LaborStatusForm.POSN_CODE == 'S41119'))
    
    celtsLaborDict = {}
    for usr in celtsLabor:
        if usr.studentName not in celtsLaborDict:
            celtsLaborDict[usr.studentName] = []
        celtsLaborDict[usr.studentName].append((usr.termCode_id, usr.POSN_TITLE, usr.POSN_CODE))


    return jsonify(celtsLaborDict)