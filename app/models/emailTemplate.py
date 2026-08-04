from app.models import *


class EmailTemplate (baseModel):
    emailTemplateID                 = PrimaryKeyField()
    purpose                         = CharField()
    formType                        = CharField()
    action                          = CharField()
    subject                         = CharField()
    body                            = CharField(max_length=10000)
    audience                        = CharField()


#since idk where to store this information-Kat:
#Emails in labor status form:
#LSF
#1:When labor status form is submitted: send to student
#2:When LSF is approved: send to supervisor and student and academic advisor
#3:When LSF is rejected: send to supervisor and student
#4:When LSF is adjusted: send to supervisor and student (?)
#Pending
#5:When a pending form is modified: send to supervisor and student
#LRF
#6:When labor release form is submitted: Send to student
#7:When lrf is approved: send to supervisor and student and academic advisor
#8:When lrf is rejected: send to supervisor and student
#Overload
#9: When labor overload form submitted (by student): send to supervisor(??? and advisor???)
#10: When labor overload approved: send to supervisor and student(??? and advisor???)
#11: When laber overload rejected: send to supervisor and student (??? and advisor???)
