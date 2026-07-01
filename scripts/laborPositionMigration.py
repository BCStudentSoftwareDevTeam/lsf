from io import BytesIO
import mammoth
from boxsdk import OAuth2, Client

auth = OAuth2(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
)

client = Client(auth)

folder_id = "YOUR_FOLDER_ID"

def getBoxFolder(folderID):
    return client.folder(folderID).get()


def getBoxFiles(folder):
    return folder.get_items()


def parseDocument(box_file):
    memory_file = BytesIO()

    box_file.download_to(memory_file)
    memory_file.seek(0)
    result = mammoth.extract_raw_text(memory_file)
    return result.value

def checkDocumentExist(documentName):
    # TODO: Check if the document already exists in your database
    return False

def migrateDocument():
    folder = getBoxFolder(folder_id)
    for item in getBoxFiles(folder):
        if item.type != "file":
            continue
        if not item.name.endswith(".docx"):
            continue
        print(f"Processing: {item.name}")
        if checkDocumentExist(item.name):
            print("Already exists.")
            continue
        text = parseDocument(item)
        print(text)

        # TODO:
        # Save text to database here

migrateDocument()