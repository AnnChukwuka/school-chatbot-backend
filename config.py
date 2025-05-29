import os
import json
from firebase_admin import credentials, initialize_app
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








cred_json = os.getenv("FIREBASE_CRED_JSON")
if not cred_json:
    raise RuntimeError("Missing FIREBASE_CRED_JSON environment variable")

# Convert escaped \n back to actual newlines
cred_dict = json.loads(cred_json)
cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")

cred = credentials.Certificate(cred_dict)
initialize_app(cred)




