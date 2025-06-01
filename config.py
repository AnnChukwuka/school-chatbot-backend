import os
import firebase_admin
from firebase_admin import credentials, initialize_app
from config import API_KEY
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────
# Paths & Directories
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

TXT_DIR = BASE_DIR / "school_data"
INDEX_FILE = BASE_DIR / "faiss_index.index"
METADATA_FILE = BASE_DIR / "faiss_metadata.json"
MODEL_PATH = os.getenv("MODEL_PATH", BASE_DIR / "models/llama-2-7b-chat.Q4_K_M.gguf")



# ─────────────────────────────────────────────
# OpenAI (Optional Fallback)
# ─────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key-here")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
API_KEY = os.getenv("API_KEY")


# main.py or firebase_config.py

firebase_config = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
}

import firebase_admin

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

