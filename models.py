class Email:
    def __init__(self, subject, receivers, html_msg, filepath=None, filename=None):
        self.subject = subject
        self.receivers = receivers
        self.html_msg = html_msg
        self.filepath = filepath
        self.filename = filename
