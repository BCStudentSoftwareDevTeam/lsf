from app.models.Tracy import *


class STUSTAFF(baseModel):
	PIDM  		= CharField(primary_key=True)
	ID  		= CharField(null=True)		# B-number
	FIRST_NAME  = CharField(null=True)
	LAST_NAME  	= CharField(null=True)
	EMAIL  		= CharField(null=True)
	CPO  		= CharField(null=True)
	ORG  		= CharField(null=True)
	DEPT_NAME  	= CharField(null=True)

	def __str__(self):
		return str(self.__dict__)
