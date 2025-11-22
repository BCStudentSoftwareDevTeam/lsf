import pprint
from peewee import DoesNotExist
from app.logic.tracy import Tracy
from app.models.term import Term
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.controllers.admin_routes.termManagement import createTerms
import import_functions as importf

importf.DEBUG = False

# Beforehand, clean up data
# :%s/ctrl-v u0092/'/g
# :%s/ctrl-v ctrl-r/,/g
# :%s/&amp;/\&/g

print("Creating terms...")
createTerms(2015)
createTerms(2016)
createTerms(2017)
createTerms(2018)
createTerms(2019)
createTerms(2020)
Term.get_or_create(termCode=201905, termName="Spring COVID-19 Closure 2020",isBreak=True)


# past forms
past_fields = [
        'form_id', # internal id
        'primarySupervisor', # bnumber, only has a value sometimes
        'PrimarySupervisorName', # text, only has a value sometimes
        'created_on', # null at the beginning, then datetime string with ms
        'job_type', # Primary, Secondary, Secondary (Break Labor)
        'supervisee', # student bnumber
        'superviseeName', # student name
        'supervisor', # staff bnumber
        'supervisorName', # staff name
        'creator', # username
        'term', # term title
        'posn_code', # position code
        'positionName', # position name
        'hour', # contract hours (only a per-day value. grrr) or weekly hours
        'WLS', # WLS number
        'start', # contract start
        'end', # contract end
        'approval', # 1 for approved, -1 for rejected, empty for pending?
        'rejectReason', # text for rejection
        'department', # department text
        'departmentCode', # department #
        'processedBy', # username
        'processedDate', # datetime string with ms
        'departmentAccount', # number. what's the difference between this and department code?
        'note' # text note
        ]
current_fields = [
        'primarySupervisor', # bnumber. only has a value sometimes
        'created_on', # datetime string with ms
        'job_type', # Primary or Secondary
        'supervisee', # student bnumber
        'supervisor', # staff bnumber
        'creator', # username
        'term', # term title
        'posn_code', # position code
        'hour', # hours (contract or weekly)
        'form_id', # internal ID
        'start', # contract start
        'end', # contract end
        'note' # text note
        ]

def import_file(filepath, fields):
    with open(filepath,'r',encoding="cp1252",newline='') as reader:
        print("Importing {}...".format(filepath))
        print("  * Validating...")
        if importf.validate_file(reader, fields):
            print("  * Getting records...")
            data = importf.getList(reader, fields)
            saved = 0
            terms = {}
            print("  * Creating forms...")
            for record in data:
                if importf.importRecord(record, terms):
                    saved += 1
                    print(".", end="", flush=True)
                    if saved % 100 == 0:
                        print(str(saved).rjust(8))
                else:
                    print("X", end="", flush=True)

            print("\nCreated {} forms\n".format(saved))
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(terms)

import_file('pastlsf5.csv', past_fields)
import_file('lsf5.csv', current_fields)
