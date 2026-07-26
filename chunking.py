"""
chunking.py
-----------
Splits long documents (e.g. a whole resume PDF's text) into smaller,
overlapping chunks suitable for embedding and retrieval.

Why chunking matters for RAG:
- Too large a chunk -> retrieval becomes fuzzy (a chunk might be "mostly"
  relevant but dilute the actual answer with unrelated text).
- Too small a chunk -> you lose context (e.g. splitting a sentence in half).
- Overlap between consecutive chunks prevents losing information that sits
  right at a chunk boundary.

Strategy used here: paragraph-aware sliding window.
  1. Split on paragraph breaks first (natural semantic boundaries).
  2. Merge small paragraphs together until close to CHUNK_SIZE.
  3. If a single paragraph is longer than CHUNK_SIZE, fall back to a
     character-based sliding window with overlap.
"""

from config import CHUNK_SIZE, CHUNK_OVERLAP


def _split_long_paragraph(paragraph: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(paragraph):
        end = start + chunk_size
        chunks.append(paragraph[start:end])
        start = end - overlap  # step forward, but re-include the overlap
    return chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        # Fall back to line breaks if the PDF extraction didn't preserve blank lines
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            # Flush whatever we've built up so far
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_split_long_paragraph(paragraph, chunk_size, overlap))
            continue

        if len(current) + len(paragraph) + 1 <= chunk_size:
            current = f"{current}\n{paragraph}".strip()
        else:
            chunks.append(current.strip())
            current = paragraph

    if current:
        chunks.append(current.strip())

    return [c for c in chunks if c]


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Takes [{"text": ..., "source": ...}, ...] and returns a flat list of
    chunk dicts: [{"text": chunk, "source": source, "chunk_id": i}, ...]
    """
    all_chunks = []
    for doc in documents:
        pieces = chunk_text(doc["text"])
        for i, piece in enumerate(pieces):
            all_chunks.append({
                "text": piece,
                "source": doc["source"],
                "chunk_id": i,
            })

    print(f"[chunking] Produced {len(all_chunks)} chunks from {len(documents)} documents.")
    return all_chunks
