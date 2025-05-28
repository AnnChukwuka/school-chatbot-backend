# scripts/export_unknown_queries.py
import datetime
from firebase_admin import firestore
from config import firebase_config  # This ensures Firebase is initialized via config.py

db = firestore.client()

OUTPUT_FILE = "unknown_queries_export.txt"
RESET_HANDLED = False

def export_unknown_queries():
    if RESET_HANDLED:
        for doc in db.collection("unknown_queries").stream():
            doc.reference.update({"handled": False})

    query_stream = db.collection("unknown_queries").where("handled", "==", False).stream()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for doc in query_stream:
            message = doc.to_dict().get("message", "").strip()
            if message:
                f.write(f"- {message}\n")
                doc.reference.update({"handled": True})

    print(f"\n Exported unknown queries to {OUTPUT_FILE}")

if __name__ == "__main__":
    export_unknown_queries()
