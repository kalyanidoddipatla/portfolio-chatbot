# Portfolio AI Assistant — Modular RAG Chatbot (v2)

An upgraded version of the single-file chatbot: instead of a hardcoded
knowledge base, this version ingests your **resume PDF, LinkedIn PDF
export, and GitHub repos**, chunks them properly, embeds them with
Gemini, and stores everything in a **persistent ChromaDB vector
database** — so embeddings survive restarts and don't need recomputing
every time the app launches.

## Setup

1. `pip install -r requirements.txt`
2. Create `.env` (see `.env.example`) with your Gemini + Pushover keys.
3. Add your files to `data/`:
   - `resume.pdf` — export your resume as a PDF
   - `linkedin.pdf` — LinkedIn profile → "More" → "Save to PDF"
   - `github.txt` — a single line with your GitHub username or profile URL
4. Build the index (do this once, and again any time your files change):
   ```
   python build_index.py
   ```
5. Launch the chatbot:
   ```
   python app.py
   ```

## File-by-file

| File | Responsibility |
|---|---|
| `config.py` | All env vars, paths, and model names in one place |
| `document_loader.py` | Reads PDFs/text files, fetches GitHub repo data via API |
| `chunking.py` | Splits raw text into overlapping, paragraph-aware chunks |
| `embeddings.py` | Wraps Gemini's embedding API (document vs. query task types) |
| `vector_store.py` | Builds/queries the persistent ChromaDB collection |
| `build_index.py` | One-off script: run whenever `data/` changes |
| `tools.py` | Pushover notifications + tool-calling functions |
| `chat_engine.py` | Retrieval + Gemini chat + tool-calling loop |
| `app.py` | Thin Gradio UI layer |

## Why this structure

Each file has exactly one job. If you swap Gemini for another embedding
provider, you only touch `embeddings.py`. If you swap Gradio for a Flask
API, you only touch `app.py`. If you change how chunking works, you only
touch `chunking.py`. This separation is what makes the codebase
maintainable as it grows — and it's a clean answer if an interviewer
asks how you structured the project.

## Notes

- `build_index.py` fully **wipes and rebuilds** the ChromaDB collection
  each time it runs — safe to re-run any time your source files change.
- GitHub repo fetching skips private repos and forks automatically, and
  turns each public repo into its own retrievable chunk (name,
  description, language, topics, stars).
- If a PDF's text doesn't extract cleanly (e.g. it's a scanned image),
  `document_loader.py` will warn you in the console — in that case,
  export a text-based PDF instead of a scanned/image one.
