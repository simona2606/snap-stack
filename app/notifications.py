import logging
import smtplib
from email.message import EmailMessage
from config import load_config
import os

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

        # Load sender email and password from environment variables
        sender_email = os.getenv('EMAIL_SENDER')
        app_password = os.getenv('EMAIL_APP_PASSWORD')

        # Use recipient from the configuration or default to one passed explicitly
        recipient = recipient or config["email"]["recipient_email"]

        smtp_server = config["email"]["smtp_server"]
        smtp_port = config["email"]["smtp_port"]

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)

        logging.info(f"Email sent to {recipient} with subject: {subject}")
    except Exception as e:
        logging.error(f"Error in sending the email: {e}")

