"""
Utils file
"""
import os
import requests
import smtplib, ssl
import logging
import json

from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


log = logging.getLogger(__name__)


def validate_user_credentials(username, password):
    """
    validate credentials
    """
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(username, password)
    except smtplib.SMTPAuthenticationError as error:
        raise error


def generate_email_data(sender_email, draw_data):
    """
    Convert data into the smtp email message format
    Arguments:
        sender_email: (str) to email
        draw_data: list(dict)
            Example:
                [
                    {
                            "name": "Ali",
                            "email": "xyz@gmail.com",
                            "cc": [],
                            "draw": 100,
                            "date": "2022-01-16",
                            "body": '<p></p>',
                    },
                    {
                            "name": "Kamran",
                            "email": "abc@gmail.com",
                            "cc:: [],
                            "draw": 700,
                            "date": "2022-02-16",
                            "body": '<p></p>',
                    }
                ]
    Returns:
       list of messages
            [
                {
                    "email": "xyz@gmail.com",
                    "message": "<html>...</html>"
                },
                {
                    "email": "abc@gmail.com",
                    "message": "<html>...</html>"
                }
            ]
    """
    email_data = []
    for draw_item in draw_data:
        if draw_item.get("email"):
            message = MIMEMultipart("alternative")
            environment = Environment(loader=FileSystemLoader("templates/"))
            if draw_item["body"]:
                message["Subject"] = "Congratulations!"
                template = environment.get_template("win.txt")
            else:
                message["Subject"] = "Better Luck Next Time..."
                template = environment.get_template("lose.txt")
            content = template.render(
                name=draw_item["name"],
                draw=draw_item["draw"],
                date=draw_item["date"],
                bond_details=draw_item["body"],
            )
            message["From"] = sender_email
            message["To"] = draw_item["email"]
            message["CC"] = ",".join(draw_item["cc"])
            mime_html = MIMEText(content, "html")
            message.attach(mime_html)
            message_data = {
                "email": draw_item["email"],
                "cc": draw_item["cc"],
                "message": message.as_string(),
            }
            email_data.append(message_data)
    return email_data


def send_mails(sender_email, sender_password, email_data):
    """
    Login to the smtp server and send emails to users
    """
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        for message_data in email_data:
            try:
                server.sendmail(
                    sender_email,
                    [message_data["email"]] + [message_data["cc"]],
                    message_data["message"],
                )
                log.info(f'Email sent to {message_data["email"]}')
            except:
                log.warning(f'Error in sending email to {message_data["email"]}')


def load_json(source):
    """
    load the data from the source, ther it's a local path or the
    """
    # Check if the source is a local file path
    if os.path.isfile(source):
        with open(source, "r") as file:
            data = json.load(file)
        return data
    # Otherwise, assume it's a URL
    else:
        try:
            response = requests.get(source)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the JSON from URL: {e}")
            return None
