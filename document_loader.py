"""
document_loader.py
-------------------
Turns raw source files in data/ into plain text "documents" ready for
chunking. Each document is a dict: {"text": ..., "source": ...}

Supports:
  - PDFs (resume.pdf, linkedin.pdf) via pypdf
  - Plain text files (.txt)
  - GitHub profile -> fetches public repo names/descriptions via the
    GitHub REST API (no auth needed for public data, but rate-limited)
"""

import os
import re
import requests
from pypdf import PdfReader

from config import DATA_DIR


def load_pdf(path: str) -> str:
    """Extract all text from a PDF, page by page."""
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def extract_github_username(text: str) -> str:
    """Pull a username out of either a raw username or a full github.com URL."""
    text = text.strip()
    match = re.search(r"github\.com/([A-Za-z0-9-]+)", text)
    if match:
        return match.group(1)
    return text  # assume it's already just a username


def fetch_github_repos(github_txt_path: str) -> list[dict]:
    """
    Reads data/github.txt (containing a username or profile URL), calls the
    public GitHub API, and returns one "document" per repository so each
    repo becomes its own retrievable chunk.
    """
    if not os.path.exists(github_txt_path):
        return []

    raw = load_text_file(github_txt_path)
    username = extract_github_username(raw)
    if not username:
        return []

    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        repos = response.json()
    except requests.RequestException as e:
        print(f"[document_loader] Could not fetch GitHub repos: {e}")
        return []

    documents = []
    for repo in repos:
        if repo.get("private") or repo.get("fork"):
            continue  # skip private repos and forks — keep the KB focused

        name = repo.get("name", "unknown")
        description = repo.get("description") or "No description provided."
        language = repo.get("language") or "Not specified"
        stars = repo.get("stargazers_count", 0)
        topics = ", ".join(repo.get("topics", [])) or "none"

        text = (
            f"GitHub repository: {name}. "
            f"Description: {description}. "
            f"Primary language: {language}. "
            f"Topics: {topics}. "
            f"Stars: {stars}."
        )
        documents.append({"text": text, "source": f"github:{name}"})

    return documents


def load_all_documents() -> list[dict]:
    """
    Scans DATA_DIR for resume.pdf, linkedin.pdf, github.txt (and any other
    .pdf/.txt files you add), and returns a list of {"text", "source"} dicts.
    """
    documents = []

    if not os.path.isdir(DATA_DIR):
        print(f"[document_loader] Data folder not found: {DATA_DIR}")
        return documents

    for filename in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, filename)

        if filename.lower() == "github.txt":
            documents.extend(fetch_github_repos(path))

        elif filename.lower().endswith(".pdf"):
            text = load_pdf(path)
            if text.strip():
                documents.append({"text": text, "source": filename})
            else:
                print(f"[document_loader] Warning: no extractable text in {filename}")

        elif filename.lower().endswith(".txt"):
            text = load_text_file(path)
            if text.strip():
                documents.append({"text": text, "source": filename})

    print(f"[document_loader] Loaded {len(documents)} source documents.")
    return documents
