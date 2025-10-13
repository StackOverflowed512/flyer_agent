import logging
from flyer_sender import send_flyer_via_email
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_email_sending():
    # Test sending email
    TEST_EMAIL = "pict.vaishnav@gmail.com"
    TEST_PRODUCT = "Email-Response-Prediction"  # or "PPE-Detection"

    # Verify environment variables
    if not all([os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD")]):
        logger.error("Missing email credentials in .env file")
        return False

    print(f"Attempting to send email to {TEST_EMAIL}...")
    try:
        result = send_flyer_via_email(TEST_EMAIL, TEST_PRODUCT)
        if result:
            print("Email sent successfully!")
        else:
            print("Failed to send email. Check the logs for details.")
        return result
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    test_email_sending()
