from flask import current_app, render_template
from flask_mail import Message
from . import mail
from threading import Thread

def send_async_email(app, msg):
    """Sends asynchronous email notifications via Python.

    Args:
        app (class - Flask app): The application you are using
        msg (string): The email you are sending
    """
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    """Sends email notifications to the user/recipient

    Args:
        to (class): The specified user in the database
        subject (string): Will show up in the subject line of the email
        template (string): The file that holds your email template to send, which is either appended
        with ".txt" or ".html"
    """
    app = current_app._get_current_object()
    msg = Message(
        subject=app.config['CARDAGAIN_MAIL_SUBJECT_PREFIX'] + subject,
        recipients=[to],
        sender=app.config['CARDAGAIN_MAIL_SENDER']
    )

    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()