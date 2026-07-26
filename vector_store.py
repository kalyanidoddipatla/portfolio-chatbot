"""
vector_store.py
----------------
Manages the persistent vector database (ChromaDB). This is the upgrade
from the earlier "in-memory NumPy list" version — embeddings are now
written to disk under chroma_db/, so they survive restarts and don't
need to be recomputed every time the app launches.

Two entry points:
  - build_index()      -> wipes and rebuilds the collection from data/
                           (run this via build_index.py whenever your
                           resume/LinkedIn/GitHub content changes)
  - retrieve(query, k)  -> embeds a live question and returns the top-k
                            most relevant chunks (used by chat_engine.py)
"""

import chromadb

from config import CHROMA_DIR, COLLECTION_NAME, TOP_K
from document_loader import load_all_documents
from chunking import chunk_documents
from embeddings import embed_documents, embed_query

_client = chromadb.PersistentClient(path=CHROMA_DIR)


def _get_collection(reset: bool = False):
    if reset:
        try:
            _client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # collection didn't exist yet — fine
    return _client.get_or_create_collection(COLLECTION_NAME)


def build_index():
    """
    Full pipeline: load documents from data/ -> chunk -> embed -> store.
    Wipes any existing collection first, so this is safe to re-run any
    time your source files change.
    """
    documents = load_all_documents()
    if not documents:
        print("[vector_store] No documents found in data/. Nothing to index.")
        return

    chunks = chunk_documents(documents)
    texts = [c["text"] for c in chunks]

    print(f"[vector_store] Embedding {len(texts)} chunks...")
    vectors = embed_documents(texts)

    collection = _get_collection(reset=True)
    collection.add(
        ids=[f"{c['source']}-{c['chunk_id']}" for c in chunks],
        documents=texts,
        embeddings=vectors,
        metadatas=[{"source": c["source"]} for c in chunks],
    )

    print(f"[vector_store] Index built: {len(texts)} chunks stored in '{COLLECTION_NAME}'.")


def retrieve(query: str, top_k: int = TOP_K) -> list[str]:
    """Return the top_k most relevant chunk texts for a given query."""
    collection = _get_collection(reset=False)

    if collection.count() == 0:
        print("[vector_store] Warning: collection is empty. Run build_index.py first.")
        return []

    query_vector = embed_query(query)
    results = collection.query(query_embeddings=[query_vector], n_results=top_k)
    return results["documents"][0] if results["documents"] else []
