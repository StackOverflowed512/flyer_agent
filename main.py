import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import re
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database import init_db, save_customer_data
from mistral_client import get_mistral_response
from flyer_sender import send_flyer_via_email, send_flyer_via_whatsapp

# --- FastAPI App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Mount static files directory (for CSS, JS)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize Jinja2 templates for rendering HTML
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# --- Health Check Endpoint for Render ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- Pydantic Models for Data Validation ---
class ChatRequest(BaseModel):
    message: str
    history: list

# --- API Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main HTML page for the chatbot UI."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    """Handles incoming chat messages from the user."""
    try:
        bot_response = get_mistral_response(chat_request.message, chat_request.history)
        customer_data = extract_customer_data(chat_request.history + [
            {"role": "user", "content": chat_request.message},
            {"role": "assistant", "content": bot_response}
        ])
        
        # Check if this message is about sending a flyer
        if any(word in chat_request.message.lower() for word in ['yes', 'sure', 'send', 'email', 'flyer']):
            # Find the product name from conversation history
            product_name = None
            for msg in chat_request.history:
                content = msg['content'].lower()
                if "email-response-prediction" in content.lower():
                    product_name = "Email-Response-Prediction"
                    break
                elif "ppe-detection" in content.lower() or "ppe" in content.lower():
                    product_name = "PPE-Detection"
                    break
            
            if customer_data and customer_data.get('email') and product_name:
                logger.info(f"Attempting to send flyer to {customer_data['email']} for {product_name}")
                try:
                    success = send_flyer_via_email(customer_data['email'], product_name)
                    if success:
                        bot_response = f"Great! I've sent the {product_name} flyer to your email address ({customer_data['email']}). Please check your inbox. Is there anything else I can help you with?"
                    else:
                        bot_response = "I apologize, but there was an issue sending the flyer. Please try again or provide a different email address."
                        logger.error(f"Failed to send flyer to {customer_data['email']}")
                except Exception as e:
                    logger.error(f"Error sending flyer: {str(e)}")
                    bot_response = "I apologize, but there was an error sending the flyer. Please try again later."
            elif not customer_data.get('email'):
                bot_response = "I don't have your email address yet. Could you please provide it?"
            elif not product_name:
                bot_response = "Which product flyer would you like? (Email-Response-Prediction or PPE-Detection)"

        # Save customer data if available
        if customer_data:
            save_customer_data(customer_data)

        return {"response": bot_response}

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def extract_customer_data(history):
    """Extracts customer data from conversation history."""
    data = {}
    
    # Combine all conversation content for analysis
    full_conversation = " ".join([msg['content'] for msg in history])
    
    # Extract email using regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, full_conversation)
    if email_match:
        data['email'] = email_match.group()
    
    # Extract name
    name_patterns = [
        r"my name is\s+([A-Za-z]+)",
        r"name is\s+([A-Za-z]+)",
        r"i'm\s+([A-Za-z]+)",
        r"im\s+([A-Za-z]+)",
        r"this is\s+([A-Za-z]+)"
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, full_conversation.lower())
        if name_match:
            data['name'] = name_match.group(1).title()
            break
    
    # Extract location
    location_keywords = ["from", "location", "based in", "in"]
    for msg in history:
        content_lower = msg['content'].lower()
        for keyword in location_keywords:
            if keyword in content_lower:
                # Try to extract location after the keyword
                parts = content_lower.split(keyword)
                if len(parts) > 1:
                    potential_location = parts[1].strip().split('.')[0].split(',')[0].split(' ')[0]
                    if potential_location and len(potential_location) > 1:
                        data['location'] = potential_location.title()
                        break
    
    # Extract WhatsApp number using regex
    whatsapp_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    whatsapp_matches = re.findall(whatsapp_pattern, full_conversation)
    for match in whatsapp_matches:
        if match and len(''.join(filter(str.isdigit, match))) >= 10:
            data['whatsapp'] = ''.join(filter(str.isdigit, match))
            break
    
    return data

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)