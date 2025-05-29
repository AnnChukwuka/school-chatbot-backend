# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from intent_handler import detect_intent, intent_responses, save_chat_message, log_unknown_query
from config import OPENAI_API_KEY, OPENAI_MODEL
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # for local dev
        "https://school-chatbot-frontend.vercel.app",  # production domain
        "https://school-chatbot-frontend-q1ge013d5-annchukwukas-projects.vercel.app",  # this specific deploy too
    ],
    allow_credentials=True,
    allow_methods=["*"],  # must allow HEAD, OPTIONS, POST
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    log_to_firebase: Optional[bool] = True

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
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
        answer = intent_responses[intent]
        if req.log_to_firebase:
            save_chat_message(session_id, answer, "bot")
        return ChatResponse(answer=answer)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
        model=OPENAI_MODEL,
     messages=[
        {
            "role": "system",
            "content": (
                "You are Azalea, a friendly university assistant at BAU. "
                "Answer any academic, school-related, or general student questions helpfully."
            )
        },
        {"role": "user", "content": q}
    ]
)
      
        reply = response.choices[0].message.content.strip()
        if req.log_to_firebase:
            save_chat_message(session_id, reply, "bot")
        return ChatResponse(answer=reply)
    except Exception as e:
        print(" OpenAI fallback failed:", e)
        fallback = "Sorry, I couldn't find an answer to that."
        if req.log_to_firebase:
            save_chat_message(session_id, fallback, "bot")
        return ChatResponse(answer=fallback)
