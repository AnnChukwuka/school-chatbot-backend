# backend/main.py

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional                    
from uuid import uuid4
from intent_handler import detect_intent, intent_responses, get_response, save_chat_message, log_unknown_query
from config import OPENAI_API_KEY, OPENAI_MODEL, API_KEY
from openai import OpenAI
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import firestore

app = FastAPI()

# Updated CORS Middleware to allow dynamic Vercel URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://school-chatbot-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = firestore.client()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    log_to_firebase: Optional[bool] = True

class ChatResponse(BaseModel):
    answer: str

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    q = req.message
    session_id = req.session_id or str(uuid4())
    print(f"Incoming message: {q}")

    if req.log_to_firebase:
        save_chat_message(session_id, q, "user")

    intent = detect_intent(q)
    if intent == "unknown":
        log_unknown_query(q)

    if intent and intent in intent_responses and intent != "unknown":
        answer = get_response(intent)  
        if req.log_to_firebase:
            save_chat_message(session_id, answer["text"], "bot")
        return JSONResponse(content=answer)  

    # fallback OpenAI
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Azalea, a friendly university assistant at Bahcesehir Cyprus University. "
                        "Answer any academic, school-related, or general student questions helpfully."
                    )
                },
                {"role": "user", "content": q}
            ]
        )

        reply = response.choices[0].message.content.strip()
        if req.log_to_firebase:
            save_chat_message(session_id, reply, "bot")
        return JSONResponse(content={"type": "text", "text": reply})  # fallback always text
    except Exception as e:
        print("OpenAI fallback failed:", e)
        fallback = "Sorry, I couldn't find an answer to that."
        if req.log_to_firebase:
            save_chat_message(session_id, fallback, "bot")
        return JSONResponse(content={"type": "text", "text": fallback})


@app.get("/chat/history")
async def get_chat_history(session_id: str, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    ref = db.collection("chats").document(session_id).collection("messages")
    query = ref.order_by("timestamp")
    docs = query.stream()
    history = [{"sender": doc.get("sender"), "text": doc.get("text")} for doc in docs]
    return {"history": history}

@app.post("/chat/clear")
async def clear_chat_history(data: dict, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    session_id = data.get("session_id")
    ref = db.collection("chats").document(session_id).collection("messages")
    docs = ref.stream()
    for doc in docs:
        doc.reference.delete()
    return {"message": "Chat history cleared"}

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
