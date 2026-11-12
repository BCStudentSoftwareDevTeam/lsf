from io import BytesIO
import mammoth
from boxsdk import OAuth2, Client
from peewee import DoesNotExist
from app.models.positionHistory import PositionHistory
import re
from bs4 import BeautifulSoup
from app.models.positionDescriptionSection import PositionDescriptionSection
from datetime import date

auth = OAuth2(
    client_id=" ",
    client_secret=" ",
    access_token=" ",
)

client = Client(auth)
folder_id = "405069205932"

from app.models.department import Department

from datetime import date


def resolveRevisionDate(year):
    """Use January 1 as the import convention for year-only revisions."""
    return date(int(year), 1, 1)

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

def getBoxFolder(folderID):
    """
    Get a Box folder using its folder ID.
    """
    return client.folder(folderID).get()


def getBoxFiles(folder):
    """
    Return the items contained directly inside a Box folder.
    """
    return folder.get_items(limit=1000)


SECTION_HEADINGS = {
    "wls level justification": "WLS Level Justification",
    "description of duties for this position":
        "Description of Duties for This Position",
    "learning opportunities for this position":
        "Learning Opportunities for This Position",
    "qualifications needed for this position":
        "Qualifications Needed for This Position",
}


def normalizeHeading(text):
    # Remove prefixes such as "II.", "III.", or "IV."
    text = re.sub(r"^\s*[IVXLCDM]+\.\s*", "", text)
    return text.strip().rstrip(":").casefold()


def parseDocument(boxFile):
    """
    Extract position metadata and ordered description sections.

    Section content is retained as HTML to preserve lists and formatting.
    """
    memoryFile = BytesIO()
    boxFile.download_to(memoryFile)
    memoryFile.seek(0)

    result = mammoth.convert_to_html(memoryFile)

    for message in result.messages:
        print(f"Mammoth warning: {message}")

    soup = BeautifulSoup(result.value, "html.parser")
    documentText = soup.get_text(separator="\n", strip=True)

    def requiredValue(pattern, label):
        match = re.search(pattern, documentText, flags=re.IGNORECASE)

        if not match:
            raise ValueError(f"Missing or invalid {label} in {boxFile.name}")

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
        "wls": int(requiredValue(
            r"WLS Level:\s*(\d+)\b",
            "numeric WLS level",
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
        heading = SECTION_HEADINGS.get(normalizeHeading(text))

        if heading:
            currentSection = {
                "sectionTitle": heading,
                "content": [],
            }
            sections.append(currentSection)

        elif currentSection is not None and text:
            currentSection["content"].append(str(element))

    if not sections:
        raise ValueError(f"No recognized sections in {boxFile.name}")

    metadata["sections"] = [
        {
            "sectionTitle": section["sectionTitle"],
            "sectionContent": "\n".join(section["content"]),
            "order": index,
        }
        for index, section in enumerate(sections, start=1)
    ]

    return metadata


def saveDocument(document, department, revisionDate, revisedBy, status):
    """
    Create a position and its sections together.

    Repeated imports skip an existing position with the same unique key.
    """
    if revisionDate.year != document["revisionYear"]:
        raise ValueError("Revision date does not match the document's year")

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
    organizationNumber=None,
    positionCode=None,
    wls=None,
    revisionYear=None,
    revisedBy="Box import",
    status="Active",
):
    folder = getBoxFolder(folder_id)

    for item in getBoxFiles(folder):
        if item.type != "file" or not item.name.lower().endswith(".docx"):
            continue

        try:
            boxFile = client.file(item.id).get()
            document = parseDocument(boxFile)

            # Skip documents that don't match the supplied filters.
            if (
                organizationNumber is not None
                and document["organizationNumber"] != str(organizationNumber)
            ):
                continue

            if (
                positionCode is not None
                and document["positionCode"] != positionCode
            ):
                continue

            if wls is not None and document["wls"] != int(wls):
                continue

            if (
                revisionYear is not None
                and document["revisionYear"] != int(revisionYear)
            ):
                continue

            department = resolveDepartment(
                document["organizationNumber"]
            )

            revisionDate = resolveRevisionDate(
                document["revisionYear"]
            )

            position, created = saveDocument(
                document=document,
                department=department,
                revisionDate=revisionDate,
                revisedBy=revisedBy,
                status=status,
            )

            action = "Saved" if created else "Skipped existing"
            print(f"{action}: {position.positionTitle}")

        except Exception as error:
            print(f"Failed to migrate {item.name}: {error}")


def testBoxConnection():
    currentUser = client.user().get()
    print(f"Connected to Box as: {currentUser.name}")

    folder = client.folder(folder_id).get()
    print(f"Folder found: {folder.name}")

    print("Folder items:")
    for item in client.folder(folder_id).get_items(limit=100):
        print(f"- {item.name} ({item.type})")


if __name__ == "__main__":
    testBoxConnection()
    # Import everything.
    migrateDocument()

    # # Import only one department.
    # migrateDocument(organizationNumber="2114")

    # # Import only WLS 2 positions.
    # migrateDocument(wls=2)

    # # Import one specific position.
    # migrateDocument(positionCode="S85405")

    # # Combine filters: all supplied conditions must match.
    # migrateDocument(
    #     organizationNumber="2114",
    #     wls=2,
    #     revisionYear=2025,
    # )