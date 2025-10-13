import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
import os
from dotenv import load_dotenv

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
if SENDER_EMAIL and SENDER_EMAIL.startswith('"') and SENDER_EMAIL.endswith('"'):
    SENDER_EMAIL = SENDER_EMAIL[1:-1]
if SENDER_PASSWORD and SENDER_PASSWORD.startswith('"') and SENDER_PASSWORD.endswith('"'):
    SENDER_PASSWORD = SENDER_PASSWORD[1:-1]

def send_email(to_email: str, subject: str, body: str) -> bool:
    """Sends an email using Gmail SMTP."""
    if not all([SENDER_EMAIL, SENDER_PASSWORD, to_email]):
        logger.error("Missing required email parameters")
        return False

    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            
            # Try to login
            try:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
            except smtplib.SMTPAuthenticationError:
                logger.error("Gmail authentication failed. Check your credentials and ensure 'Less secure app access' is enabled")
                return False
            
            # Send the email
            server.send_message(msg)
            logger.info(f"Email sent successfully to {to_email}")
            return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Gmail authentication failed. Error: {e}")
        logger.error("Please ensure you're using an App Password if 2FA is enabled")
        return False
    except Exception as e:
        logger.error(f"Failed to send email. Error details: {str(e)}")
        return False

def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: str) -> bool:
    """Sends an email with attachment using Gmail SMTP."""
    if not all([SENDER_EMAIL, SENDER_PASSWORD, to_email, attachment_path]):
        logger.error(f"Missing parameters. SENDER_EMAIL: {bool(SENDER_EMAIL)}, PASSWORD: {bool(SENDER_PASSWORD)}, TO: {bool(to_email)}, PATH: {bool(attachment_path)}")
        return False

    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        # Add body
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Verify attachment exists
        if not os.path.exists(attachment_path):
            logger.error(f"Attachment not found at: {attachment_path}")
            return False

        # Add attachment
        with open(attachment_path, 'rb') as f:
            part = MIMEApplication(f.read(), _subtype="pdf")
            part.add_header('Content-Disposition', 'attachment', 
                          filename=os.path.basename(attachment_path))
            msg.attach(part)

        # Use SSL connection
        logger.info(f"Connecting to SMTP server for {to_email}")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            logger.info(f"Email sent successfully to {to_email}")
            return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Authentication failed. Make sure to use App Password: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False