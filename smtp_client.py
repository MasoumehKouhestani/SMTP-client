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

        self.smtp_connection = self.connect(config)

    def connect(self, config):
        smtp_connection = smtplib.SMTP(config['host'], config['port'])
        if config.get('tls', True):
            smtp_connection.starttls()
        self.authenticate(smtp_connection)

        return smtp_connection

    def authenticate(self, smtp_connection):
        smtp_connection.login(self.username, self.password)

    def send_email(self, mail: Email, quite_connection=True):
        # create the meta data
        meta_data = mail.meta_data or []
        if type(meta_data) not in (tuple, list):
            meta_data = [meta_data]

        # Create a text/plain message
        msgs = []
        for i, addr in enumerate(mail.receivers):
            msg = MIMEMultipart()
            msg['Subject'] = email.header.Header(force_str(mail.subject), 'utf-8')
            msg['From'] = self.from_email
            msg['To'] = addr

            # Add AWS headers
            if self.provider == 'AWS':
                if settings.SES_CONFIGURATION_SET:
                    msg['X-SES-CONFIGURATION-SET'] = settings.SES_CONFIGURATION_SET

            # The main body is just another attachment
            body = MIMEText(mail.html_msg.encode('utf-8'), 'html', 'utf-8')
            msg.attach(body)
            if mail.filepath:
                # PDF attachment
                fp = open(mail.filepath, 'rb')
                att = MIMEApplication(fp.read(), _subtype="csv")
                fp.close()
                att.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=mail.filename
                )
                msg.attach(att)
            msgs.append(msg)

        # send via Gmail server
        i = 0
        current_retry = 0
        while i < len(msgs):
            msg = msgs[i]
            try:
                self.smtp_connection.sendmail(msg['From'], [msg['To']], msg.as_string())
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
