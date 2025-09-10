import pytest
from app import app
from flask_mail import Mail, Message

with app.app_context():
    msg = Message("Test Email", recipients=["laborstatusform-aaaaazdxy4j2lsinl67ikumy4y@studentprogrammers.slack.com"],html="<h3>Test</h3>Whooo",sender="support@bereacollege.onmicrosoft.com")
    mail = Mail(app)

    ("Sending")
    mail.send(msg)
    ("Sent")
