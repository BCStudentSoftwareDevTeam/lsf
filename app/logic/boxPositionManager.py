from datetime import date
from io import BytesIO
import re

import mammoth
from boxsdk import OAuth2, Client
from bs4 import BeautifulSoup

from app.models.department import Department
from app.models.positionHistory import PositionHistory
from app.models.positionDescriptionSection import PositionDescriptionSection


class BoxPositionImporter:
    SECTION_HEADINGS = {
        "wls level justification": "WLS Level Justification",
        "description of duties for this position":
            "Description of Duties for This Position",
        "learning opportunities for this position":
            "Learning Opportunities for This Position",
        "qualifications needed for this position":
            "Qualifications Needed for This Position",
    }

    def __init__(
        self,
        clientID,
        clientSecret,
        accessToken,
        folderID="405069205932",
    ):
        auth = OAuth2(
            client_id=clientID,
            client_secret=clientSecret,
            access_token=accessToken,
        )

        self.client = Client(auth)
        self.folderID = folderID

    @staticmethod
    def resolveRevisionDate(year):
        """Use January 1 as the import convention for year-only revisions."""
        return date(int(year), 1, 1)

    @staticmethod
    def resolveDepartment(organizationNumber):
        org = str(organizationNumber).strip()

        matches = list(
            Department.select()
            .where(Department.ORG == org)
            .limit(2)
        )

        if not matches:
            raise ValueError(f"No department found for ORG {org}")

        if len(matches) > 1:
            raise ValueError(f"Multiple departments found for ORG {org}")

        return matches[0]

    def getBoxFolder(self):
        """Get the configured Box folder."""
        return self.client.folder(self.folderID).get()

    @staticmethod
    def getBoxFiles(folder):
        """Return items contained directly inside a Box folder."""
        return folder.get_items(limit=1000)

    @staticmethod
    def normalizeHeading(text):
        """Remove prefixes such as II., III., or IV."""
        text = re.sub(r"^\s*[IVXLCDM]+\.\s*", "", text)
        return text.strip().rstrip(":").casefold()

    def parseDocument(self, boxFile):
        """
        Extract position metadata and ordered description sections.

        Retain section content as HTML to preserve lists and formatting.
        """
        with BytesIO() as memoryFile:
            boxFile.download_to(memoryFile)
            memoryFile.seek(0)
            result = mammoth.convert_to_html(memoryFile)

        for message in result.messages:
            print(f"Mammoth warning: {message}")

        soup = BeautifulSoup(result.value, "html.parser")
        documentText = soup.get_text(separator="\n", strip=True)

        def requiredValue(pattern, label):
            match = re.search(
                pattern,
                documentText,
                flags=re.IGNORECASE,
            )

            if not match:
                raise ValueError(
                    f"Missing or invalid {label} in {boxFile.name}"
                )

            return match.group(1).strip()

        metadata = {
            "positionTitle": requiredValue(
                r"Position Title:\s*([^\n]+)",
                "position title",
            ),
            "positionCode": requiredValue(
                r"Position Code:\s*([^\s]+)",
                "position code",
            ),
            "departmentName": requiredValue(
                r"Department Name:\s*(.+?)(?=\s*Org\.\s*#)",
                "department name",
            ),
            "organizationNumber": requiredValue(
                r"Org\.\s*#:\s*(\d+)",
                "organization number",
            ),
            "wls": self.parseWls(requiredValue(
                r"WLS Level:\s*(Special|[1-7])\b",
                "WLS level",
            )),
            "revisionYear": int(requiredValue(
                r"Current Revision Year:\s*(\d{4})\b",
                "revision year",
            )),
        }

        sections = []
        currentSection = None

        for element in soup.find_all(recursive=False):
            text = element.get_text(" ", strip=True)
            heading = self.SECTION_HEADINGS.get(
                self.normalizeHeading(text)
            )

            if heading:
                currentSection = {
                    "sectionTitle": heading,
                    "content": [],
                }
                sections.append(currentSection)

            elif currentSection is not None and text:
                currentSection["content"].append(str(element))

        if not sections:
            raise ValueError(
                f"No recognized sections in {boxFile.name}"
            )

        metadata["sections"] = [
            {
                "sectionTitle": section["sectionTitle"],
                "sectionContent": "\n".join(section["content"]),
                "order": index,
            }
            for index, section in enumerate(sections, start=1)
        ]

        return metadata

    @staticmethod
    def parseWls(value):
        if str(value).strip().casefold() == "special":
            return 7

        wls = int(value)

        if wls not in range(1, 8):
            raise ValueError("WLS must be 1–6 or Special")

        return wls

    @staticmethod
    def saveDocument(
        document,
        department,
        revisionDate,
        revisedBy,
        status,
    ):
        """
        Create a new history record only when its unique key is new.

        Existing records and their sections are left unchanged.
        """
        if revisionDate.year != document["revisionYear"]:
            raise ValueError(
                "Revision date does not match the document's year"
            )

        database = PositionHistory._meta.database

        with database.atomic():
            position, created = PositionHistory.get_or_create(
                positionCode=document["positionCode"],
                revisionDate=revisionDate,
                status=status,
                defaults={
                    "positionTitle": document["positionTitle"],
                    "department": department,
                    "wls": document["wls"],
                    "revisedBy": revisedBy,
                },
            )

            if created:
                for section in document["sections"]:
                    PositionDescriptionSection.create(
                        position=position,
                        **section,
                    )

        return position, created

    def migrateDocument(
        self,
        departmentID=None,
        wls=None,
        revisionStart=None,
        revisionEnd=None,
        revisedBy="Box import",
        status="Active",
        allowedDepartmentIDs=None,
    ):
        """
        Import matching documents within an inclusive revision date range.

        revisionStart and revisionEnd must be date objects or None.
        """
        if (
            revisionStart is not None
            and revisionEnd is not None
            and revisionStart > revisionEnd
        ):
            raise ValueError(
                "The start date must be on or before the end date."
            )

        selectedDepartment = (
            Department.get_by_id(departmentID)
            if departmentID is not None
            else None
        )

        selectedWls = self.parseWls(wls) if wls is not None else None

        allowedIDs = (
            {int(value) for value in allowedDepartmentIDs}
            if allowedDepartmentIDs is not None
            else None
        )

        if (
            selectedDepartment is not None
            and allowedIDs is not None
            and selectedDepartment.departmentID not in allowedIDs
        ):
            raise ValueError(
                "Department is not available for import"
            )

        summary = {
            "imported": 0,
            "existing": 0,
            "filtered": 0,
            "failed": 0,
            "errors": [],
        }

        folder = self.getBoxFolder()

        for item in self.getBoxFiles(folder):
            if (
                item.type != "file"
                or not item.name.lower().endswith(".docx")
            ):
                continue

            try:
                boxFile = self.client.file(item.id).get()
                document = self.parseDocument(boxFile)

                if (
                    selectedDepartment is not None
                    and document["organizationNumber"]
                    != str(selectedDepartment.ORG).strip()
                ):
                    summary["filtered"] += 1
                    continue

                if (
                    selectedWls is not None
                    and document["wls"] != selectedWls
                ):
                    summary["filtered"] += 1
                    continue

                # Current documents supply a year only.
                # resolveRevisionDate converts it to January 1.
                revisionDate = self.resolveRevisionDate(
                    document["revisionYear"]
                )

                if (
                    revisionStart is not None
                    and revisionDate < revisionStart
                ):
                    summary["filtered"] += 1
                    continue

                if (
                    revisionEnd is not None
                    and revisionDate > revisionEnd
                ):
                    summary["filtered"] += 1
                    continue

                department = self.resolveDepartment(
                    document["organizationNumber"]
                )

                if (
                    allowedIDs is not None
                    and department.departmentID not in allowedIDs
                ):
                    summary["filtered"] += 1
                    continue

                position, created = self.saveDocument(
                    document=document,
                    department=department,
                    revisionDate=revisionDate,
                    revisedBy=revisedBy,
                    status=status,
                )

                if created:
                    summary["imported"] += 1
                else:
                    summary["existing"] += 1

            except Exception as error:
                summary["failed"] += 1
                summary["errors"].append({
                    "file": item.name,
                    "message": str(error),
                })

        return summary

    def testBoxConnection(self):
        currentUser = self.client.user().get()
        print(f"Connected to Box as: {currentUser.name}")

        folder = self.getBoxFolder()
        print(f"Folder found: {folder.name}")

        print("Folder items:")
        for item in folder.get_items(limit=100):
            print(f"- {item.name} ({item.type})")

    def uploadFile(self, filePath, fileName=None, folderID=None):
        """
        Upload a local file to Box.

        Defaults to the configured folder and original filename.
        Returns the uploaded Box File object.
        """
        folder = self.client.folder(
            self.folderID if folderID is None else folderID
        )

        return folder.upload(
            file_path=str(filePath),
            file_name=fileName,
        )

    def uploadStream(self, stream, fileName, folderID=None):
        """
        Upload a binary stream, such as BytesIO or a Flask upload.

        The stream must be positioned at the start of the content.
        Returns the uploaded Box File object.
        """
        folder = self.client.folder(
            self.folderID if folderID is None else folderID
        )

        return folder.upload_stream(
            file_stream=stream,
            file_name=fileName,
        )

if __name__ == "__main__":
    importer = BoxPositionImporter(
        clientID=" ",
        clientSecret=" ",
        accessToken=" ",
        folderID="405069205932",
    )

    importer.testBoxConnection()

    # Import everything.
    importer.migrateDocument()

    # Import only one department.
    # importer.migrateDocument(organizationNumber="2114")

    # Import only WLS 2 positions.
    # importer.migrateDocument(wls=2)

    # Import one specific position.
    # importer.migrateDocument(positionCode="S85405")

    # Combine filters: all supplied conditions must match.
    # importer.migrateDocument(
    #     organizationNumber="2114",
    #     wls=2,
    #     revisionYear=2025,
    # )