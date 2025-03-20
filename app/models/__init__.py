import os

from peewee import *

from app import app

def getMySQLDB():
    if os.environ.get("USING_CONTAINER", False):
        app.config['lsfdb']['host'] = 'db'
    else:
        app.config["lsfdb"]["host"] = "localhost"
    theDB = MySQLDatabase(app.config['lsfdb']['db_name'], host = app.config['lsfdb']['host'], user = app.config['lsfdb']['username'], passwd = app.config['lsfdb']['password'])
    return theDB

mainDB = getMySQLDB() # MySQL (current)

class baseModel(Model):
    class Meta:
        database = mainDB
