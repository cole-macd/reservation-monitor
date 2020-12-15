import ssl

from email.message import EmailMessage
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

class SMS:
    def __init__(self, number, phone_carrier, username, password):
        self.CARRIERS = {
            'tmobile': '@tmomail.net',
            'telus': '@msg.telus.com',
            'rogers': '@pcs.rogers.com',
            'bell': '@txt.bell.ca'
        }
        self.EMAIL_DOMAIN = 'smtp.gmail.com'

        self.receiver_email = f'{number}{self.CARRIERS.get(phone_carrier)}'
        self.username = username
        self.password = password
            
        self.server = SMTP_SSL(self.EMAIL_DOMAIN)
        self.server.login(self.username, self.password)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.quit()

    def send(self, message_text, message_subject):
        try:
            message = MIMEText(message_text)
            message['From'] = self.username
            message['To'] = self.receiver_email
            message['Subject'] = message_subject

            print("Sending message to %s" % self.receiver_email)
            self.server.send_message(message)

        except Exception as e:
            print(f'send error: {e}')
