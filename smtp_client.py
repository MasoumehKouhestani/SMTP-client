import email
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

from django.conf import settings
from django.utils.encoding import force_str

from models import Email


class SmtpClientService:

    max_retry = 2
    required_config_fields = ['username', 'password', 'host', 'port']

    def __init__(self, from_email=settings.DEFAULT_FROM_EMAIL, reply_email=None, config=settings.DEFAULT_EMAIL_CONFIG):

        self.from_email = from_email
        self.reply_email = reply_email
        self.provider = config.get('provider')

        self.username = config['username']
        self.password = config['password']

        self.smtp_connection = self._connect(config)

    def _connect(self, config):
        smtp_connection = smtplib.SMTP(config['host'], config['port'])
        if config.get('tls', True):
            smtp_connection.starttls()
        self._authenticate(smtp_connection)

        return smtp_connection

    def _authenticate(self, smtp_connection):
        smtp_connection.login(self.username, self.password)

    def send_email(self, mail: Email, quite_connection=True):
        # Create a text/plain message
        messages = []
        for _, receiver in enumerate(mail.receivers):
            message = MIMEMultipart()
            message['Subject'] = email.header.Header(force_str(mail.subject), 'utf-8')
            message['From'] = self.from_email
            message['To'] = receiver

            # Add AWS headers
            if self.provider == 'AWS':
                if settings.SES_CONFIGURATION_SET:
                    message['X-SES-CONFIGURATION-SET'] = settings.SES_CONFIGURATION_SET

            # The main body is just another attachment
            body = MIMEText(mail.html_msg.encode('utf-8'), 'html', 'utf-8')
            message.attach(body)

            if mail.filepath:
                # PDF attachment
                file = open(mail.filepath, 'rb')
                file_attribute = MIMEApplication(file.read(), _subtype="csv")
                file.close()
                file_attribute.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=mail.filename
                )
                message.attach(file_attribute)
            messages.append(message)

        # send via Gmail server
        i = 0
        current_retry = 0
        while i < len(messages):
            message = messages[i]
            try:
                self.smtp_connection.sendmail(message['From'], [message['To']], message.as_string())
                current_retry = 0
                i += 1
            except smtplib.SMTPResponseException as e:
                if e.smtp_code == 454 and current_retry < self.max_retry:
                    current_retry += 1
                    sleep(1)
                    continue
                raise e

        if quite_connection:
            self.quite()

    def quite(self):
        self.smtp_connection.quit()
