import os
from dotenv import load_dotenv
from email_utils import send_email_with_attachment
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# --- Email Sending Logic ---
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Flyer file paths
FLYERS_DIR = Path(__file__).parent / "flyers"
FLYERS = {
    "Email-Response-Prediction": FLYERS_DIR / "email_response_prediction.pdf",
    "PPE-Detection": FLYERS_DIR / "ppe_detection.pdf"
}

def send_flyer_via_email(recipient_email, product_name):
    """Sends product flyer via email."""
    if not recipient_email or not product_name:
        logger.error("Missing recipient email or product name")
        return False

    try:
        subject = f"Your Requested {product_name} Product Flyer"
        body = f"""Dear Valued Customer,

Thank you for your interest in our {product_name} product. Please find the product flyer attached to this email.

If you have any questions, please don't hesitate to reply to this email.

Best regards,
AI Product Assistant"""
        
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            logger.error("Missing email credentials in .env file")
            return False

        if product_name not in FLYERS:
            logger.error(f"Invalid product name: {product_name}")
            return False

        flyer_path = FLYERS[product_name]
        
        # Create flyers directory if it doesn't exist
        if not FLYERS_DIR.exists():
            FLYERS_DIR.mkdir(parents=True)
            logger.warning("Created missing flyers directory")
            
        # Create a placeholder PDF if the flyer doesn't exist
        if not flyer_path.exists():
            from create_flyers import create_placeholder_flyer
            logger.warning(f"Creating placeholder flyer for {product_name}")
            create_placeholder_flyer(
                str(flyer_path),
                product_name,
                COMPANY_PRODUCTS.get(product_name, "Product information not available.")
            )
            
        success = send_email_with_attachment(
            recipient_email, 
            subject, 
            body, 
            str(flyer_path)
        )
        
        if success:
            logger.info(f"Product flyer email sent successfully to {recipient_email}")
            return True
        else:
            logger.error(f"Failed to send product flyer email to {recipient_email}")
            return False
            
    except Exception as e:
        logger.error(f"Error in send_flyer_via_email: {str(e)}")
        return False

def send_flyer_via_whatsapp(whatsapp_number):
    """Placeholder function to simulate sending a flyer via WhatsApp."""
    print(f"Flyer link sent to WhatsApp number: {whatsapp_number}")
    # In a real application, this would integrate with a WhatsApp API
    return True