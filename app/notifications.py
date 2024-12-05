import logging
import smtplib
from email.message import EmailMessage

# Logger Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Write logs to file
        logging.StreamHandler()         # Show logs to console
    ]
)

def send_email(subject, body, recipient="simonaettari@libero.it"):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = 'your_email@gmail.com'
        msg['To'] = recipient

        # SMTP Configuration of Gmail
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587  # SMTP port of Gmail
        gmail_user = 'simonaTest23@gmail.com'
        gmail_password = 'rqsj obct otjo vcsh'  # Use an "App Password" for security

        # Connection to SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()  # Enable TLS Encryption
            smtp.login(gmail_user, gmail_password)
            smtp.send_message(msg)

        logging.info(f"Email sent to {recipient} with subject: {subject}")
    except Exception as e:
        logging.error(f"Error in sending the email: {e}")

