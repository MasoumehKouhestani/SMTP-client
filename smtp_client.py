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
        messages = []
        for _, receiver in enumerate(mail.receivers):
            messages.append(self._create_message(mail, receiver))

        self._send_mail(messages)

        if quite_connection:
            self.quite()

    def _create_message(self, mail, receiver):
        message = MIMEMultipart()
        message['Subject'] = email.header.Header(force_str(mail.subject), 'utf-8')
        message['From'] = self.from_email
        message['To'] = receiver

        # Add AWS headers
        if self.provider == 'AWS':
            if settings.SES_CONFIGURATION_SET:
                message['X-SES-CONFIGURATION-SET'] = settings.SES_CONFIGURATION_SET

        message.attach(self._create_main_body_message(mail.html_msg))

        if mail.filepath:
            file_attribute = self._create_file_attachment(mail.filepath, mail.filename)
            message.attach(file_attribute)

        return message

    def _create_main_body_message(self, html_msg):
        return MIMEText(html_msg.encode('utf-8'), 'html', 'utf-8')

    def _create_file_attachment(self, filepath, filename):
        file = open(filepath, 'rb')
        file_attribute = MIMEApplication(file.read(), _subtype="csv")
        file.close()
        file_attribute.add_header(
            'Content-Disposition',
            'attachment',
            filename=filename
        )
        return file_attribute

    def _send_mail(self, messages):
        current_retry = 0
        for i in range(len(messages)):
            message = messages[i]
            try:
                self.smtp_connection.sendmail(message['From'], [message['To']], message.as_string())
                current_retry = 0
            except smtplib.SMTPResponseException as e:
                if e.smtp_code == 454 and current_retry < self.max_retry:
                    current_retry += 1
                    sleep(1)
                    continue
                raise e

    def quite(self):
        self.smtp_connection.quit()
