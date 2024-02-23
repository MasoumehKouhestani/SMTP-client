import smtplib
from unittest import TestCase
from unittest.mock import patch

from imap_tools import MailBoxUnencrypted
from imap_tools.message import MailMessage

import settings
from smtp_client import Email, SmtpClientService


def read_last_mail(username, password, host="localhost", port=3143) -> MailMessage:
    with MailBoxUnencrypted(host, port).login(username, password) as mailbox:
        return list(mailbox.fetch())[-1]


class SMTPClientTest(TestCase):

    subject = "test subject"
    receiver = "receiver@example.com"
    html_msg = "sample message"

    def test_smtp_client(self):
        reply_email = "another@mail.com"
        service = SmtpClientService(reply_email=reply_email)

        file_path = "tests/test_data/test.csv"
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
        self.assertEqual(settings.SES_CONFIGURATION_SET, mail.headers.get("X-SES-CONFIGURATION-SET".lower())[0])

    def test_smtp_client_with_no_attachments(self):
        service = SmtpClientService()

        mail = Email(self.subject, [self.receiver], self.html_msg)
        service.send_email(mail)

        mail = read_last_mail(username=self.receiver, password=self.receiver)

        self.assertIsNotNone(mail)
        self.assertEqual(self.subject, mail.subject)
        self.assertEqual(self.html_msg, mail.html)
        self.assertEqual(0, len(mail.attachments))

    def test_smtp_client_fail_sending_more_than_max_retry(self):
        failure_code = 454
        failure_message = "Connection refused!"
        with patch.object(
            smtplib.SMTP, "send_message", side_effect=smtplib.SMTPResponseException(failure_code, failure_message)
        ) as mock_send_message:
            with self.assertRaises(smtplib.SMTPResponseException) as e:
                service = SmtpClientService()

                receivers = [self.receiver]
                mail = Email(self.subject, receivers, self.html_msg)
                service.send_email(mail)
            exception_message = "({}, '{}')".format(failure_code, failure_message)
            self.assertEqual(exception_message, str(e.exception))
            self.assertEqual(settings.DEFAULT_EMAIL_CONFIG["max_retry"], mock_send_message.call_count)
