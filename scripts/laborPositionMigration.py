from io import BytesIO
import mammoth
from boxsdk import OAuth2, Client
from peewee import DoesNotExist
from app.models.positionHistory import PositionHistory

auth = OAuth2(
    client_id="",
    client_secret="",
    access_token="",
)

client = Client(auth)
folder_id = ""


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


def parseDocument(boxFile):
    """
    Download a Word document into memory and extract its plain text.
    """
    memoryFile = BytesIO()
    boxFile.download_to(memoryFile)
    memoryFile.seek(0)
    result = mammoth.convert_to_html(memoryFile)
    if result.messages:
        for message in result.messages:
            print(f"Mammoth warning: {message}")
    return result.value.strip()


def saveDocument(boxFile, documentText):
    """
    Save the Box document information and extracted text to the database.
    """
    return PositionHistory.create()


def migrateDocument():
    """
    Download each DOCX file from the Box folder, extract its text,
    and insert it into the database.
    """
    folder = getBoxFolder(folder_id)

    for item in getBoxFiles(folder):
        if item.type != "file":
            continue

        if not item.name.lower().endswith(".docx"):
            continue

        print(f"Processing: {item.name}")

        try:
            # Get the complete Box file object, including metadata.
            boxFile = client.file(item.id).get()

            documentText = parseDocument(boxFile)

            if not documentText:
                print(f"No text found in: {boxFile.name}")
                continue

            savedDocument = saveDocument(boxFile, documentText)

            print(
                f"Saved: {savedDocument.documentName} "
                f"with database ID {savedDocument.id}"
            )

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
    migrateDocument()