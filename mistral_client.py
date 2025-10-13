import os
from mistralai import Mistral
from dotenv import load_dotenv
import time
import random

# --- Mistral AI API Configuration ---
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY not found. Please set it in the .env file.")

client = Mistral(api_key=api_key)
model = "mistral-large-latest"

# --- Product Information ---
# This dictionary contains the company's product catalog.
# The AI will use this information to suggest relevant products.
COMPANY_PRODUCTS = {
    "Email-Response-Prediction": "An AI tool that predicts email responses and helps optimize email campaigns.",
    "PPE-Detection": "An advanced computer vision system for detecting proper use of Personal Protective Equipment in workplaces."
}

def get_mistral_response(user_message, conversation_history):
    """
    Calls the Mistral AI API to get a response based on the user's message and conversation history.

    Args:
        user_message (str): The latest message from the user.
        conversation_history (list): A list of previous messages in the conversation.

    Returns:
        str: The chatbot's response.
    """
    max_retries = 3
    base_delay = 1  # Base delay in seconds
    
    for attempt in range(max_retries):
        try:
            # The system prompt guides the AI's behavior and defines its role.
            system_prompt = f"""
            You are an AI Product Assistant for an AI software company. Your goal is to greet the user, understand their business needs, collect their contact information (Name, Location, Email, WhatsApp), suggest a relevant product from the list below, and then ask if they want a product flyer.

            Available Products:
            - Email-Response-Prediction: {COMPANY_PRODUCTS['Email-Response-Prediction']}
            - PPE-Detection: {COMPANY_PRODUCTS['PPE-Detection']}

            Conversation Flow:
            1. Greet the user warmly.
            2. Ask for their business requirement.
            3. Once they provide their requirement, ask for their Name.
            4. Then ask for their Location.
            5. Then ask for their Email.
            6. Then ask for their WhatsApp number.
            7. Ask which product they are interested in (Email-Response-Prediction or PPE-Detection).
            8. Ask if they want the product flyer sent to their Email or WhatsApp.
            9. If they agree, confirm the delivery method.
            10. Be conversational and friendly throughout.
            """
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add the conversation history to the messages
            for msg in conversation_history:
                messages.append({"role": msg['role'], "content": msg['content']})
            
            # Add the latest user message
            messages.append({"role": "user", "content": user_message})

            # Add exponential backoff delay after first attempt
            if attempt > 0:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(delay)

            chat_response = client.chat.complete(
                model=model,
                messages=messages
            )
            
            return chat_response.choices[0].message.content

        except Exception as e:
            if "service_tier_capacity_exceeded" in str(e):
                if attempt == max_retries - 1:
                    return "I'm experiencing high traffic at the moment. Please try again in a few minutes."
                continue
            else:
                print(f"Error calling Mistral API: {e}")
                return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again later."