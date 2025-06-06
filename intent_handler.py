# scripts/intent_handler.py

import json  # load JSON
import string
import datetime
import firebase_admin
from firebase_admin import firestore
from config import firebase_config
from difflib import get_close_matches  # For better fuzzy matching

db = firestore.client()

# Load intents.json
with open('scripts/intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

intent_keywords = intents['intent_keywords']
phrase_keywords = intents['phrase_keywords']
intent_responses = intents['intent_responses']

def save_chat_message(session_id: str, text: str, sender: str, image: str = None):
    chat_data = {
        "session_id": session_id,
        "text": text,
        "sender": sender,
        "timestamp": datetime.datetime.utcnow(),
    }
    if image:
        chat_data["image"] = image

    db.collection("chats").add(chat_data)

def preprocess_input(user_input):
    user_input = user_input.lower().strip()
    user_input = user_input.translate(str.maketrans('', '', string.punctuation))
    return user_input.split()

def log_unknown_query(user_input: str):
    db.collection("unknown_queries").add({
        "message": user_input,
        "timestamp": datetime.datetime.utcnow(),
        "handled": False
    })

def detect_intent(user_input):
    tokens = preprocess_input(user_input)
    user_input_text = ' '.join(tokens)

    # First try keyword matching
    for intent, keywords in intent_keywords.items():
        if any(word in tokens for word in keywords):
            print(f"Matched keyword intent: {intent}")
            return intent

    # Then phrase matching with fuzzy matching
    user_input_text = user_input.lower()
    for intent, phrases in phrase_keywords.items():
        lower_phrases = [p.lower() for p in phrases]
        matches = get_close_matches(user_input_text, lower_phrases, n=1, cutoff=0.6)
        if matches:
            print(f"Matched phrase intent: {intent}")
            return intent

    log_unknown_query(user_input)
    return "unknown"

def get_response(intent):
    response = intent_responses.get(intent)
    if isinstance(response, dict):
        return {
            "type": "text_image",
            "text": response.get("text", ""),
            "image": response.get("image", "")
        }
    else:
        return {
            "type": "text",
            "text": response
        }
