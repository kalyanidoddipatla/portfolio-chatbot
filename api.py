"""
api.py
------
FastAPI backend that exposes the existing chat_engine logic as a REST API,
and serves the custom HTML/CSS/JS frontend (frontend/) as static files.

This replaces app.py (Gradio) as the entry point when using the custom
frontend. All the actual logic (retrieval, Gemini calls, tool calling)
is untouched — this file is purely a thin HTTP layer on top of it.

Run locally:  uvicorn api:app --reload
Deploy:       uvicorn api:app --host 0.0.0.0 --port $PORT
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chat_engine import chat
from vector_store import ensure_index_built

app = FastAPI(title="Personal AI Assistant API")

# Allow the frontend (served from the same origin, but useful if you ever
# host the frontend separately) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str


@app.on_event("startup")
def on_startup():
    ensure_index_built()


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    reply = chat(req.message, req.history)
    return ChatResponse(reply=reply)


# Serve the custom frontend at "/" — must be mounted LAST so it doesn't
# shadow the /api/chat route above.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
