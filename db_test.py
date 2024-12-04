import pyodbc
from app import load_config

cfg = load_config('app/config/secret_config.yaml')
details = cfg['tracy']

# details = {
#     "user": "ute_limited",
#     "password": "REPLACE",
#     "server": "timemachine1sql.berea.edu",
#     "db": "UTE"
# }

# works
pyodbc_uri = f"DRIVER=FreeTDS;SERVER={details['mssql_host']};PORT=1433;DATABASE={details['db_name']};UID={details['mssql_user']};PWD={details['mssql_password']};TDS_Version=8.0;"
             
# works
#pyodbc_uri = 'DRIVER=FreeTDS;DSN=tracyDSN;UID={};PWD={};'.format(details['user'], details['password'])
pyconn = pyodbc.connect(pyodbc_uri)
c = pyconn.cursor()
for row in c.execute('select * from STUPOSN'):
    print("PYODBC:",row)
    break

##########

from urllib.parse import quote
import sqlalchemy

# SAWarning: No driver name specified; this is expected by PyODBC when using DSN-less connections
#uri = "mssql+pyodbc://{}:{}@{}/{}".format(details['user'], details['password'], details['server'], details['db'])

# No driver name specified
#uri = "mssql+pyodbc://{}:{}@{}/{}?DRIVER=FreeTDS".format(details['user'], details['password'], details['server'], details['db'])
uri = "mssql+pyodbc:///?odbc_connect=" + quote(f"DRIVER=FreeTDS;SERVER={details['mssql_host']};PORT=1433;DATABASE={details['db_name']};UID={details['mssql_user']};PWD={details['mssql_password']};TDS_Version=8.0;")

engine = sqlalchemy.create_engine(uri)
for row in engine.execute('select * from STUPOSN'):
    print("SQLALCHEMY:",row)
    break

##########

from flask_sqlalchemy import SQLAlchemy
from app import load_config, app
from app.logic.tracy import Tracy

cfg = load_config('app/config/secret_config.yaml')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

uri = "mssql+pyodbc:///?odbc_connect=" + quote(f"DRIVER=FreeTDS;SERVER={details['mssql_host']};PORT=1433;DATABASE={details['db_name']};UID={details['mssql_user']};PWD={details['mssql_password']};TDS_Version=8.0;")

app.config['SQLALCHEMY_DATABASE_URI'] = uri
db = SQLAlchemy(app)

print("FLASK:",Tracy().getPositionFromCode("S01015"))
