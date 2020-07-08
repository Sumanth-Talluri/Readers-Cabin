import smtplib
from email.mime.text import MIMEText


def send_mail(username, email, comment):
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = 'LOGIN ID HERE'
    password = 'PASSWORD HERE'
    message = f'<h3>New Message</h3><ul><li>Username : {username}</li><li>Email : {email}</li><li>Message : {comment}</li></ul>'

    sender_email = email
    receiver_email = "ADD EMAIL HERE"
    msg = MIMEText(message, 'html')
    msg['Subject'] = "from Reader's Cabin contact page"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # send mail
    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
