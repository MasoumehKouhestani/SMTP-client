from unittest import TestCase

from smtp import SmtpService
from imap_tools import MailBoxUnencrypted
from imap_tools.message import MailMessage


def read_last_mail(username, password, host='localhost', port=3143) -> MailMessage:
    with (MailBoxUnencrypted(host, port).login(username, password) as mailbox):
        return list(mailbox.fetch())[-1]


class SMTPClientTest(TestCase):
    def test_smtp_client(self):
        service = SmtpService()

        subject = "test subject"
        receiver = "receiver@example.com"
        html_msg = "sample message"
        file_path = "test_data/test.csv"
        file_name = "test.csv"
        service.send_email(subject=subject,
                           receiver=[receiver],
                           html_msg=html_msg,
                           filepath=file_path,
                           filename=file_name)

        mail = read_last_mail(username=receiver, password=receiver)

        self.assertIsNotNone(mail)
        self.assertEqual(subject, mail.subject)
        self.assertEqual(html_msg, mail.html)
        self.assertEqual(1, len(mail.attachments))
        self.assertEqual(file_name, mail.attachments[0].filename)
        self.assertEqual(b"c1,c2", mail.attachments[0].payload) # TODO: read from file
