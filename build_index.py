"""
build_index.py
---------------
Run this file directly whenever you add/update resume.pdf, linkedin.pdf,
or github.txt in data/:

    python build_index.py

It reads everything in data/, chunks it, embeds it, and stores it in the
persistent ChromaDB folder (chroma_db/). The chatbot itself (app.py) never
rebuilds the index on its own — it just reads whatever is already stored,
so runtime startup stays fast.
"""

from vector_store import build_index

if __name__ == "__main__":
    build_index()
