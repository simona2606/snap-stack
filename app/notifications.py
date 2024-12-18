import logging
import smtplib
from email.message import EmailMessage
from config import load_config

# Logger Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Write logs to file
        logging.StreamHandler()         # Show logs to console
    ]
)

def send_email(subject, body, recipient=None):
    try:
        config = load_config()
        email_settings = config["email"]

        recipient = recipient or email_settings["recipient_email"]

        smtp_server = email_settings["smtp_server"]
        smtp_port = email_settings["smtp_port"]
        gmail_user = email_settings["sender_email"]
        gmail_password = email_settings["app_password"]

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = gmail_user
        msg['To'] = recipient

        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(gmail_user, gmail_password)
            smtp.send_message(msg)

        logging.info(f"Email sent to {recipient} with subject: {subject}")
    except Exception as e:
        logging.error(f"Error in sending the email: {e}")

