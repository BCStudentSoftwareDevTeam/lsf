from app.models.allocation import Allocation

def getAllocation(termCode, dept):
    allocationObject = Allocation.select().where(Allocation.termCode == 202500, Allocation.department == 3, Allocation.isFinal == True).dicts().get() #FIXME
    return allocationObject

def getAllocation(termCode, dept):
    allocationObject = getAllocation(termCode, dept)
    allocationDict = {"primary_10": allocationObject["primary_10"],
                    "primary_12": allocationObject["primary_12"],
                    "primary_15": allocationObject["primary_15"],
                    "primary_20": allocationObject["primary_20"],
                    "secondary_5": allocationObject["secondary_5"],
                    "secondary_10": allocationObject["secondary_10"],
                    "breakHours": allocationObject["breakHours"],
                    "totalPrimaries": (allocationObject["primary_10"] + allocationObject["primary_12"] + allocationObject["primary_15"] + allocationObject["primary_20"]),
                    "totalSecondaries": (allocationObject["secondary_5"] + allocationObject["secondary_10"]) }
    return allocationDict

def 