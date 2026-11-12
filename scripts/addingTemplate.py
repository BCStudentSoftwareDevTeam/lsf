from app.models.emailTemplate import*

emailTemplates = {
    "laborReleaseAdminNotification": {
        "purpose": "Labor Release Form Admin Notification",
        "formType": "Labor Status Form",
        "action": "Submitted",
        "subject": "Labor Release Form Submitted",
        "body": (
            "<p>Dear <strong>@@Admin@@</strong>,</p>"
            "<p>A Labor Release Form has been submitted by "
            "<strong>@@Supervisor@@</strong> for <strong>@@Student@@</strong>. This is to notify the Labor Department so that a new labor position can be assigned for <strong>@@Student@@</strong>.</p>"
            "<p>&nbsp;</p>"
            "<p>Sincerely,</p>"
            "<p>Berea's Work College Program Office</p>"
            "<p>labor_program@berea.edu</p>"
            "<p>859-985-3611</p>"
        ),
        "audience": "Admin",
    },
    "laborStatusExpiredNotification": {
        "purpose": 'Email when Labor Status Form is expired to Supervisor',
        "formType": "Labor Status Form",
        "action": "Expired",
        "subject": "Labor Status Form Expired",
        "body": (
            "<p>Dear <strong>@@Supervisor@@</strong>,</p>"
            "<p>This email is to notify that the Labor Status Form submitted by <strong>@@Creator@@</strong> for <strong>@@Student@@</strong> has expired.</p>"
            "<p>&nbsp;</p>"
            "<p>You can resubmit the Labor Status Form for the <strong>@@Student@@</strong>.</p>"
            "<p>Sincerely,</p>"
            "<p>Berea's Work College Program Office</p>"
            "<p>labor_program@berea.edu</p>"
            "<p>859-985-3611</p>",
        ),
        "audience": "Supervisor",
    },
    "studentTemplate":{
        "purpose":'Email when Labor Status Form is expired to Student', 
        "formType":"Labor Status Form", 
        "action":"Expired", 
        "subject":'Labor Status Form Expired', 
        "body":(
            '<p>Dear <strong>@@Student@@</strong>,</p>'
            '<p>This email is to notify that the Labor Status Form submitted by <strong>@@Creator@@</strong> for you has expired.</p>'
            '<p>&nbsp;</p>'
            '<p>Please notify your supervisor <strong>@@Supervisor@@</strong> to resubmit the form.</p>'
            '<p>Sincerely,<br>Berea\'s Work College Program Office<br>labor_program@berea.edu<br>859-985-3611</p>'
        ), 
        "audience":"Student",
    }
}

def addingTemplates():
    for template in emailTemplates.values():
        if EmailTemplate.select().where(EmailTemplate.purpose == template["purpose"]).count() == 0:
            print("No email template found. Creating one.")
            EmailTemplate.create(
                purpose=template["purpose"], 
                formType=template["formType"],
                action=template["action"], 
                subject=template["subject"], 
                body=template["body"], 
                audience=template["audience"])
            print("Created email template.")

def main():
    addingTemplates()
    print("Finished adding email templates.")

if __name__ == "__main__":
    main()