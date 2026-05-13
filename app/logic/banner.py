# Relying on https://www.oracle.com/technical-resources/articles/database/python-with-database-11g.html

import oracledb
from app import app

class Banner():

    def __init__(self):
        self.conn = None

        self.database_exists = False
        if app.config['use_banner']:
            self.database_exists = True
            try:
                self.conn = oracledb.connect(
                        user=app.config["banner"]["user"],
                        password=app.config["banner"]["password"],
                        dsn="{url}:{port}/{sid}".format(**app.config["banner"]))
                print("BANNER connection initialized. Oracle version {}".format(self.conn.version))

            except Exception as err:
                print("BANNER connection failed: {}: {}".format(type(err).__name__, err))
                self.database_exists = False
                raise err

    def canConnect(self):
        return self.database_exists

    def query(self, sql):
        if self.database_exists:
            try:
                cursor = self.conn.cursor()
                cursor.execute(sql)
                return cursor.fetchall()
            except Exception as err:
                print("Error querying BANNER db:", err)
                return []
        return []

    def insert(self, formHistory):
        """
        Add an official labor status form to BANNER. If no database connection exists, this method will act as
        though the insert succeeds.

        Returns True if the insert succeeds, and False otherwise. A secondary return value also returns the execute() result.

        E.g., (result, cursor) = conn.insert(data)
        """

        if self.database_exists:
            # https://bitbucket.org/laborstudents/labor-status-forms/raw/bdcbaae27a2a13b8ff4351b1e63327c52151edf5/Admin/PendingLaborStatusForms.aspx.cs
            # All break positions should have 8 as the hours per day value.
            # Hours (PZRLABRSTAT_HOUR) cannot be null in the Banner DB

            # term_type is SUM, BRK or REG
            stmt = """INSERT INTO pzrlabrstat (PZRLABRSTAT_FORM_ID, PZRLABRSTAT_SUPERVISEE, PZRLABRSTAT_SUPERVISOR, PZRLABRSTAT_JOBTYPE, PZRLABRSTAT_POSTION, PZRLABRSTAT_HOUR, PZRLABRSTAT_CONTRACT_HRS, PZRLABRSTAT_START_DATE, PZRLABRSTAT_CREATE_DATE, PZRLABRSTAT_BREAK)
                VALUES ( :formID, :studentID, :superID, :jobType, :position, :hours, :contract_hours,
                         TO_DATE(:start_date,'yyyy-mm-dd'), systimestamp, :term_type )"""

            form = formHistory.formID
            term = form.termCode
            termType = "REG"
            contractHours = form.contractHours
            hours = form.weeklyHours
            if term.isBreak and not term.isSummer:
                termType = "BRK"
                hours = 8
            elif term.isSummer:
                termType = "SUM"
                hours = 8

            jobType = form.jobType[0] # We only want the first character, 'P' or 'S'

            params = {
                ":formID": form.laborStatusFormID,
                ":studentID": form.studentSupervisee.ID,
                ":superID": form.supervisor.ID,
                ":jobType": jobType,
                ":position": form.POSN_CODE,
                ":hours": hours,
                ":contract_hours": contractHours,
                ":start_date": str(form.startDate),
                ":term_type": termType
            }

            try:
                cursor = self.conn.cursor()
                result = cursor.execute(stmt, params)
                self.conn.commit()
                print("Form {} inserted into banner".format(form.laborStatusFormID))

            except Exception as err:
                print("Error inserting into BANNER db:", err)
                return False
        
        return True # If we got here, we are successful (even if we didn't even try to insert)
