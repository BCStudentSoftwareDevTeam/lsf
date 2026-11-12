from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from app.logic.allocationManager import (
    getBreakContracts,
    getContractedAllocations,
    getTotalAllocations,
)
from app.logic.getTerms import getTerms


def getAllocationPageData(department, academicYear=None):
    """
    Shared data source for the allocation page and Excel export.
    """
    currentAY, fallTerm, springTerm = getTerms(academicYear)

    allocations = getTotalAllocations(
        currentAY.termCode,
        department,
    )

    fallContracts = getContractedAllocations(
        fallTerm.termCode,
        department,
    )

    springContracts = getContractedAllocations(
        springTerm.termCode,
        department,
    )

    breakContracts = {
        "thanksgiving": getBreakContracts(
            currentAY.termCode + 1, department
        ),
        "winter": getBreakContracts(
            currentAY.termCode + 2, department
        ),
        "spring": getBreakContracts(
            currentAY.termCode + 3, department
        ),
        "fall": getBreakContracts(
            currentAY.termCode + 4, department
        ),
        "summer": getBreakContracts(
            currentAY.termCode + 13, department
        ),
    }

    breakContracts["total"] = sum(breakContracts.values())

    return {
        "currentAY": currentAY,
        "allocations": allocations,
        "fallContracts": fallContracts,
        "springContracts": springContracts,
        "breakContracts": breakContracts,
    }


class AllocationExcelMaker:
    """
    Generate an allocation workbook in memory.
    """

    def __init__(self, department, allocationData):
        self.department = department
        self.data = allocationData

    @staticmethod
    def appendRow(sheet, values):
        """
        Write text as literal strings rather than Excel formulas.
        Preserve numeric values as numbers.
        """
        sheet.append(values)

        for cell in sheet[sheet.max_row]:
            if isinstance(cell.value, str):
                cell.data_type = "s"

    def makeExcel(self):
        workbook = Workbook()

        self.makeSummary(workbook.active)
        self.makeDetails(workbook.create_sheet("Allocation Details"))

        for sheet in workbook.worksheets:
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions

            for cell in sheet[1]:
                cell.font = Font(bold=True)

            for index, column in enumerate(sheet.columns, start=1):
                width = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column
                )

                sheet.column_dimensions[
                    get_column_letter(index)
                ].width = min(max(width + 2, 14), 45)

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        return output

    def makeSummary(self, sheet):
        sheet.title = "Summary"

        allocations = self.data["allocations"]
        fall = self.data["fallContracts"]
        spring = self.data["springContracts"]
        breaks = self.data["breakContracts"]

        headers = [
            "Department",
            "ORG",
            "Account",
            "Academic Year",
            "Total Allocated Positions",
            "Allocated Primary Positions",
            "Allocated Secondary Positions",
            "Fall Contracted Positions",
            "Spring Contracted Positions",
            "Allocated Break Hours",
            "Total Contracted Break Hours",
            "Fall Break Contracted Hours",
            "Thanksgiving Break Contracted Hours",
            "Winter Break Contracted Hours",
            "Spring Break Contracted Hours",
            "Summer Contracted Hours",
        ]

        values = [
            self.department.DEPT_NAME,
            self.department.ORG,
            self.department.ACCOUNT,
            self.data["currentAY"].termName,
            allocations["totalAllocations"],
            allocations["totalPrimaries"],
            allocations["totalSecondaries"],
            fall["used_total"],
            spring["used_total"],
            allocations["breakHours"],
            breaks["total"],
            breaks["fall"],
            breaks["thanksgiving"],
            breaks["winter"],
            breaks["spring"],
            breaks["summer"],
        ]

        self.appendRow(sheet, headers)
        self.appendRow(sheet, values)

    def makeDetails(self, sheet):
        self.appendRow(sheet, [
            "Academic Year",
            "Period",
            "Category",
            "Unit",
            "Allocated",
            "Contracted",
        ])

        academicYear = self.data["currentAY"].termName
        allocations = self.data["allocations"]

        categories = [
            ("Primary 10 Hour", "primary_10", "used_10"),
            ("Primary 12 Hour", "primary_12", "used_12"),
            ("Primary 15 Hour", "primary_15", "used_15"),
            ("Primary 20 Hour", "primary_20", "used_20"),
            ("Total Primaries", "totalPrimaries", "used_primaries"),
            ("Secondary 5 Hour", "secondary_5", "used_5_sec"),
            ("Secondary 10 Hour", "secondary_10", "used_10_sec"),
            ("Total Secondaries", "totalSecondaries", "used_secondaries"),
            ("Total Positions", "totalAllocations", "used_total"),
        ]

        for period, contracts in (
            ("Fall", self.data["fallContracts"]),
            ("Spring", self.data["springContracts"]),
        ):
            for label, allocationKey, contractKey in categories:
                self.appendRow(sheet, [
                    academicYear,
                    period,
                    label,
                    "Positions",
                    allocations[allocationKey],
                    contracts[contractKey],
                ])

        for period, key in (
            ("Fall Break", "fall"),
            ("Thanksgiving Break", "thanksgiving"),
            ("Winter Break", "winter"),
            ("Spring Break", "spring"),
            ("Summer", "summer"),
        ):
            self.appendRow(sheet, [
                academicYear,
                period,
                "Break Hours",
                "Hours",
                None,
                self.data["breakContracts"][key],
            ])

        self.appendRow(sheet, [
            academicYear,
            "All Breaks",
            "Total Break Hours",
            "Hours",
            allocations["breakHours"],
            self.data["breakContracts"]["total"],
        ])