import email
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

from django.conf import settings
from django.utils.encoding import force_str


class SmtpClientService:

    max_retry = 2
    required_config_fields = ['username', 'password', 'host', 'port']

    def __init__(self, from_email=settings.DEFAULT_FROM_EMAIL, reply_email=None, config=settings.DEFAULT_EMAIL_CONFIG):

        self.from_email = from_email
        self.reply_email = reply_email
        self.provider = config.get('provider')

        self.username = config['username']
        self.password = config['password']

        self.s = self.connect(config)

    def connect(self, config):
        s = smtplib.SMTP(config['host'], config['port'])
        if config.get('tls', True):
            s.starttls()
        self.authenticate(s)

        return s

    def authenticate(self, s):
        s.login(self.username, self.password)

    def send_email(self, subject, receiver, html_msg, filepath=None, filename=None, q=True, md=None):

        # create the meta data
        md = md or []
        if type(md) not in (tuple, list):
            md = [md]

        # Create a text/plain message
        msgs = []
        for i, addr in enumerate(receiver):
            msg = MIMEMultipart()
            msg['Subject'] = email.header.Header(force_str(subject), 'utf-8')
            msg['From'] = self.from_email
            msg['To'] = addr

            # Add AWS headers
            if self.provider == 'AWS':
                if settings.SES_CONFIGURATION_SET:
                    msg['X-SES-CONFIGURATION-SET'] = settings.SES_CONFIGURATION_SET

            # The main body is just another attachment
            body = MIMEText(html_msg.encode('utf-8'), 'html', 'utf-8')
            msg.attach(body)
            if filepath:
                # PDF attachment
                fp = open(filepath, 'rb')
                att = MIMEApplication(fp.read(), _subtype="csv")
                fp.close()
                att.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=filename
                )
                msg.attach(att)
            msgs.append(msg)

        # send via Gmail server
        i = 0
        current_retry = 0
        while i < len(msgs):
            msg = msgs[i]
            try:
                self.s.sendmail(msg['From'], [msg['To']], msg.as_string())
                current_retry = 0
                i += 1
            except smtplib.SMTPResponseException as e:
                if e.smtp_code == 454 and current_retry < self.max_retry:
                    current_retry += 1
                    sleep(1)
                    continue
                raise e

        if q:
            self.quite()

    def quite(self):
        self.s.quit()