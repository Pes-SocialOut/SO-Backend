# Import mailing libs
import os
import smtplib
from email.message import EmailMessage

def send_email(email, subject, body):
    EMAIL_ADRESS = os.getenv('MAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADRESS
    msg['To'] = email
    msg.set_content(body)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except:
        return False
    return True