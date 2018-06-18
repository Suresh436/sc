from threading import Thread
from flask_mail import Message
from app import app, mail


def send_email(recipient, subject, body, attachment=None):
    '''
    Send a mail to a recipient. The body is usually a rendered HTML template.
    The sender's credentials has been configured in the config.py file.
    '''
    #for dev environment, override all email deliveries to developer.
    if app.config['DEBUG']:
        recipient = app.config['DEV_EMAIL']
    sender = app.config['ADMINS'][0]
    message = Message(subject, sender=sender, recipients=[recipient])
    message.html = body

    if attachment:
        with app.open_resource(attachment) as fp:
            message.attach(attachment.split('/')[-1], "application/pdf", fp.read())
    # Create a new thread
    thr = Thread(target=send_async, args=[app, message])
    thr.start()


def send_async(app, message):
    ''' Send the mail asynchronously. '''
    with app.app_context():
        mail.send(message)
