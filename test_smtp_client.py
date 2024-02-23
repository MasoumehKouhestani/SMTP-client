from unittest import TestCase

from models import Email
from smtp_client import SmtpClientService
from imap_tools import MailBoxUnencrypted
from imap_tools.message import MailMessage


def read_last_mail(username, password, host="localhost", port=3143) -> MailMessage:
    with MailBoxUnencrypted(host, port).login(username, password) as mailbox:
        return list(mailbox.fetch())[-1]


class SMTPClientTest(TestCase):

    def setUp(self):
        self.subject = "test subject"
        self.receiver = "receiver@example.com"
        self.html_msg = "sample message"

    def test_smtp_client(self):
        reply_email = "another@mail.com"
        service = SmtpClientService(reply_email=reply_email)

        file_path = "test_data/test.csv"
        file_name = "test.csv"
        mail = Email(self.subject, [self.receiver], self.html_msg, file_path, file_name)
        service.send_email(mail)

        mail = read_last_mail(username=self.receiver, password=self.receiver)

        self.assertIsNotNone(mail)
        self.assertEqual(self.subject, mail.subject)
        self.assertEqual(self.html_msg, mail.html)
        self.assertEqual(1, len(mail.attachments))
        self.assertEqual(file_name, mail.attachments[0].filename)
        file = open(file_path, "r")
        file_content = "".join(file.readlines())
        self.assertEqual(bytes(file_content, "utf-8"), mail.attachments[0].payload)
        self.assertEqual(1, len(mail.headers.get("reply-to")))
        self.assertEqual(reply_email, mail.headers.get("reply-to")[0])
