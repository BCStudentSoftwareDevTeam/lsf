import pyodbc

details = {
    "user": "ute_limited",
    "password": "REPLACE",
    "server": "timemachine1sql.berea.edu",
    "db": "UTE"
}

###########################
# Test pyodbc connection
###########################

pyodbc_uri = 'DRIVER=FreeTDS;SERVER={};PORT=1433;DATABASE={};UID={};PWD={};TDS_Version=7.4;'.format(details['server'],details['db'],details['user'],details['password'])
pyconn = pyodbc.connect(pyodbc_uri)
c = pyconn.cursor()
#for row in c.execute("select * from STUDATA where ID like '%B00815333%'"):
for row in c.execute("select * from STUPOSN"):
    print("PYODBC:",row)
    break

###########################
# Test SQL Alchemy with pyodbc
###########################

from urllib.parse import quote
import sqlalchemy

# SAWarning: No driver name specified; this is expected by PyODBC when using DSN-less connections
#uri = "mssql+pyodbc://{}:{}@{}/{}".format(details['user'], details['password'], details['server'], details['db'])

# No driver name specified
uri = "mssql+pyodbc:///?odbc_connect=" + quote('DRIVER=FreeTDS;SERVER={};PORT=1433;DATABASE={};UID={};PWD={};TDS_Version=7.4;'.format(details['server'],  details['db'], details['user'], details['password']))

engine = sqlalchemy.create_engine(uri)
with engine.connect() as connection:
    for row in connection.execute(sqlalchemy.text('select * from STUPOSN')):
        print("SQLALCHEMY:",row)
        break

###########################
# Test SQL Alchemy with app configuration
###########################

from app import app
from app.logic.tracy import Tracy

with app.test_request_context("/") as ctx:
    if app.config['use_tracy']:
        print("FLASK:",Tracy().getPositionFromCode("S01015"))
    else:
        print("FLASK: Config says not to use Tracy. Check your environment")


###########################
# Test Banner connection
###########################

from app.logic.banner import Banner
from app.models.formHistory import FormHistory
b = Banner()

if app.config['use_banner']:
    if b.database_exists:
        cursor = b.conn.cursor()
        print("BANNER",cursor)
    else:
        print("BANNER: Error with database connection")
else:
    print("BANNER: Config says not to use banner. Check your secret_config")

# NOT FOR PROD
#b.insert(FormHistory.get_by_id(39061))

