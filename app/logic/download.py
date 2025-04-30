import json
from flask import g
from app.models.formSearchResult import FormSearchResult

def saveFormSearchResult(displayName, formList, formType):
    ids = [form.formHistoryID for form in formList]

    result = FormSearchResult.create(name           = displayName,
                                     formHistoryIds = json.dumps(ids),
                                     searchType     = formType,
                                     generatedBy    = g.currentUser)

    return result.id

def retrieveFormSearchResult(formSearchResultId):
    result = FormSearchResult.get_by_id(formSearchResultId)

    # ensure we only give the result to the user who started the search
    if result.generatedBy == g.currentUser:
        return result

    return None
