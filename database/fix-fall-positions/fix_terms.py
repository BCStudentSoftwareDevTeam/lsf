from peewee import DoesNotExist
from app.models.term import Term
from app.models.laborStatusForm import LaborStatusForm
import csv

fall_term = Term.get(termCode=202011)
ay_term = Term.get(termCode=202000)

with open('activepositions.csv','r',encoding="cp1252",newline='') as f:
    print("  * Getting records...")
    reader = csv.DictReader(f, delimiter=',', restkey='extra', restval='XXXX')
    reader.__next__() # skip headers
    for row in reader:
        #print(row)
        bnumber = row['ID']
        position = row['Position']

        forms = LaborStatusForm.select().where(
                LaborStatusForm.termCode==fall_term, 
                LaborStatusForm.studentSupervisee==bnumber,
                LaborStatusForm.POSN_CODE==position)

        if not forms:
            print(f"No form found in Fall for {bnumber}, {position}")
            break

        for lsf in forms:
            print(f"Updating {position} form for {bnumber}")
            lsf.termCode = ay_term.termCode
            lsf.save()
