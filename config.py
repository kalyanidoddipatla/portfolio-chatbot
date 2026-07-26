"""
config.py
---------
Single source of truth for environment variables, file paths, and model
names. Every other module imports from here instead of reading os.environ
or hardcoding strings directly — so if you ever change a model name or a
folder path, you only change it in ONE place.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# --- API keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER = os.getenv("PUSHOVER_USER")

# --- Models ---
CHAT_MODEL = "gemini-3.5-flash"
EMBED_MODEL = "gemini-embedding-001"

# --- Paths ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "portfolio_knowledge"

# --- Chunking ---
CHUNK_SIZE = 800       # target characters per chunk
CHUNK_OVERLAP = 120    # characters of overlap between consecutive chunks

# --- Retrieval ---
TOP_K = 4  # how many chunks to retrieve per question
