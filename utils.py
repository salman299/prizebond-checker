from jinja2 import Environment, FileSystemLoader
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

log = logging.getLogger(__name__)

def send_mail(sender_email, sender_password, email, name, draw, date, body):
    message = MIMEMultipart("alternative")

    environment = Environment(loader=FileSystemLoader("templates/"))
    if body:
        message["Subject"] = "Congratulations!"
        template = environment.get_template("win.txt")
    else:
        message["Subject"] = "Better Luck Next Time..."
        template = environment.get_template("lose.txt")
    
    content = template.render(
        name=name,
        draw=draw,
        date=date,
        bond_details=body
    )
    mime_html = MIMEText(content, "html")
    
    message["From"] = sender_email
    message["To"] = email
    message.attach(mime_html)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        log.info(f'sending email to {email}')
        server.sendmail(
            sender_email, email, message.as_string()
        )
