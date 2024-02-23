# A simple SMTP client
This is a simple Python-based smtp client to send emails.

### Example
First create an Email:

    mail = Email(
            subject=<Your Subject>,
            receivers=<List of your receivers>,
            html_msg=<Your message>,
            filepath=<If you want to attach a file, your file path>,
            filename=<If you want to attach a file, along side your file path, file name here>
            )
    
Then create a smtp client with your desired configurations and call its send email method:

    DEFAULT_EMAIL_CONFIG = {
        "provider": <Your provider>,
        "username": <Your username>,
        "password": <Your password>,
        "host": <Your host>,
        "port": <Your port>,
        "tls": <True or False>,
        "max_retry": <Your maximum retry number if email sending failed>,
    }
    service = SmtpClientService(from_email=<Your base email address>,
                                reply_email=<Your reply email address if you want>, 
                                config=DEFAULT_EMAIL_CONFIG)

    service..send_email(mail, quite_connection=<set this True on last email sent>)

### Run tests
To run the tests, you should run the [greenmail](https://github.com/greenmail-mail-test/greenmail) docker to have a smtp server, with this command:

    docker run -t -i -e GREENMAIL_OPTS='-Dgreenmail.setup.test.all -Dgreenmail.hostname=0.0.0.0 -Dgreenmail.auth.disabled -Dgreenmail.verbose'            -p 3025:3025 -p 3110:3110 -p 3143:3143 -p 3465:3465 -p 3993:3993 -p 3995:3995 -p 8080:8080 greenmail/standalone

Then run the tests command to run the tests.