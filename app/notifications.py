import logging
import smtplib
from email.message import EmailMessage
from config import load_config

config = load_config()
EMAIL_SETTINGS = config["email"]

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
        recipient = recipient or EMAIL_SETTINGS["recipient_email"]

        # Usa i parametri di configurazione per la connessione SMTP
        smtp_server = EMAIL_SETTINGS["smtp_server"]
        smtp_port = EMAIL_SETTINGS["smtp_port"]
        gmail_user = EMAIL_SETTINGS["sender_email"]
        gmail_password = EMAIL_SETTINGS["app_password"]

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

