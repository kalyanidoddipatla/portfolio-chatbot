# 💬 Kalyani AI Assistant — RAG Chatbot with Gemini & Real-Time Notifications

A personal AI assistant chatbot that answers questions about my background, projects, and experience — grounded in my actual resume/LinkedIn/GitHub data via Retrieval-Augmented Generation (RAG), with real-time phone notifications whenever a visitor leaves contact details or asks something the bot can't answer.

**🔗 Live demo:** https://portfolio-chatbot-hb4j.onrender.com
*(hosted on Render's free tier — may take ~50s to wake up if idle)*

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Design Decisions](#design-decisions)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)

---

## Overview

This project started as a simple Gradio + LLM chatbot exercise and evolved into a small end-to-end AI application combining three distinct pieces of AI/backend engineering — designed as a standalone assistant that can later be embedded into a personal website:

1. **Retrieval-Augmented Generation (RAG)** — answers are grounded in real source documents, not just prompt-stuffed text
2. **Tool/function calling** — the model can autonomously trigger real side effects mid-conversation
3. **REST API integration** — three separate external APIs (Gemini, GitHub, Pushover) working together

## Features

- 🗣️ **Conversational interface** built with Gradio
- 📚 **RAG pipeline** — ingests resume PDF, LinkedIn PDF export, and live GitHub repo data; chunks, embeds, and stores them in a persistent vector database
- 🛠️ **Tool calling** — the model decides when to log an unanswerable question or capture a visitor's contact info
- 📲 **Real-time push notifications** via Pushover whenever those tools fire
- 💸 **Fully free-tier** — Gemini API (chat + embeddings) and Render hosting, no paid services required
- 🧱 **Modular codebase** — each concern (ingestion, chunking, embeddings, storage, tools, chat logic, UI) lives in its own file

## Architecture

```
Visitor sends a message
        │
        ▼
1. RETRIEVE — embed the question, compare against pre-embedded
   chunks of resume/LinkedIn/GitHub data (ChromaDB + cosine similarity)
        │
        ▼
2. AUGMENT — inject the top-matching chunks into the system prompt
   as grounding context for this turn
        │
        ▼
3. GENERATE — send [system + context, history, message] + tool
   definitions to Gemini
        │
        ▼
4. Gemini either:
     (a) answers directly using the retrieved context, or
     (b) calls a tool: record_user_details / record_unknown_question
        │
        ▼ (if a tool was called)
5. The tool fires a Pushover notification, result is returned to
   Gemini to produce a final natural-language reply
        │
        ▼
Reply shown in the Gradio chat window
```

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Gradio](https://gradio.app) `ChatInterface` |
| LLM (chat + tool calling) | Gemini 3.5 Flash, via OpenAI SDK pointed at Gemini's OpenAI-compatible endpoint |
| Embeddings | Gemini `gemini-embedding-001`, via the official `google-genai` SDK |
| Vector database | [ChromaDB](https://www.trychroma.com/) (persistent, on-disk) |
| PDF parsing | `pypdf` |
| Notifications | [Pushover](https://pushover.net) REST API |
| Source data | Resume PDF, LinkedIn PDF export, GitHub REST API |
| Hosting | [Render](https://render.com) (free tier) |
| Config | `python-dotenv` |
| Language | Python 3.14 |

## Project Structure

```
chatbot_project/
├── data/
│   ├── resume.pdf          # resume, source document for RAG
│   ├── linkedin.pdf        # LinkedIn "Save to PDF" export
│   └── github.txt          # GitHub username/URL — repos fetched live via API
│
├── config.py                # env vars, paths, model names — single source of truth
├── document_loader.py        # reads PDFs/text, fetches GitHub repo data
├── chunking.py                 # splits text into overlapping, paragraph-aware chunks
├── embeddings.py                 # wraps Gemini's embedding API
├── vector_store.py                 # builds/queries the persistent ChromaDB collection
├── build_index.py                   # one-off script — run when data/ changes
├── tools.py                           # Pushover notifications + tool-calling functions
├── chat_engine.py                       # retrieval + Gemini chat + tool-calling loop
├── app.py                                 # Gradio UI entry point
│
├── chroma_db/                               # auto-created, persisted vector store
├── requirements.txt
├── .env.example
└── README.md
```

## Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/kalyanidoddipatla/portfolio-chatbot.git
   cd portfolio-chatbot
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   python -m pip install -r requirements.txt
   ```

3. **Add your source documents** to `data/`:
   - `resume.pdf`
   - `linkedin.pdf`
   - `github.txt` (a single line: your GitHub username or profile URL)

4. **Set up environment variables** — copy `.env.example` to `.env` and fill in real values (see below)

5. **Build the vector index** (run this once, and again whenever `data/` changes)
   ```bash
   python build_index.py
   ```

6. **Run the app**
   ```bash
   python app.py
   ```
   Open the local URL Gradio prints (e.g. `http://127.0.0.1:7860`).

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Free API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `PUSHOVER_TOKEN` | API token from a Pushover Application ([pushover.net/apps/build](https://pushover.net/apps/build)) |
| `PUSHOVER_USER` | Your Pushover User Key (found on your Pushover dashboard) |

## Deployment

Deployed on **Render** (free tier):
- **Build command**: `pip install -r requirements.txt`
- **Start command**: `python app.py`
- Environment variables set via Render's dashboard (not committed to the repo)
- `app.py` binds to `0.0.0.0` and Render's assigned `$PORT`
- The vector index is rebuilt automatically on startup if missing (`ensure_index_built()` in `vector_store.py`), since Render's free tier doesn't persist disk storage across restarts

## Design Decisions

- **Why RAG instead of one big system prompt?** Small, topic-focused chunks retrieved per-question keep answers precise and scale cleanly as more source material is added, rather than relying on the model to find the relevant needle in one giant prompt.
- **Why separate embedding task types?** Gemini optimizes embeddings differently for documents (`RETRIEVAL_DOCUMENT`) vs. live queries (`RETRIEVAL_QUERY`) — this distinction is preserved throughout `embeddings.py`.
- **Why one file per concern?** Swapping any single piece (embedding provider, vector database, UI framework) only requires touching one file, not the whole codebase.
- **Why rebuild the index at startup instead of always persisting it?** Free hosting tiers (Render, HF Spaces) don't guarantee persistent disk storage between restarts — rebuilding on startup trades a few seconds of cold-start time for zero infrastructure cost.

## Known Limitations

- **Static knowledge base** — new facts require adding source content and re-running `build_index.py`; the bot can't learn mid-conversation.
- **Free-tier cold starts** — the hosted demo sleeps after ~15 minutes of inactivity and takes ~50 seconds to wake up.
- **Free-tier rate limits** — Gemini's free API tier has daily/per-minute request caps.
- **GitHub API is unauthenticated** — limited to 60 requests/hour, which is fine for occasional index rebuilds but not frequent ones.

## Roadmap

- [ ] Add a lightweight admin flow to append knowledge-base content without editing code
- [ ] Add conversation analytics to see what visitors most commonly ask
- [ ] Explore authenticated GitHub API access for higher rate limits
- [ ] Add automated tests for the chunking and retrieval logic
