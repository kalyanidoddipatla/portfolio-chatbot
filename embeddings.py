"""
embeddings.py
-------------
Thin wrapper around Gemini's embedding endpoint. Kept in its own file so
that if you ever swap embedding providers (e.g. to a local sentence-
transformers model), this is the ONLY file that needs to change.

Note the task_type distinction:
  - RETRIEVAL_DOCUMENT: used when embedding chunks going INTO the vector store
  - RETRIEVAL_QUERY:    used when embedding the user's live question
Gemini optimizes the embedding differently depending on which side of the
retrieval you're on, so keeping this distinction matters for accuracy.
"""

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, EMBED_MODEL

_client = genai.Client(api_key=GEMINI_API_KEY)


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    result = _client.models.embed_content(
        model=EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    return result.embeddings[0].values


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed a batch of chunks for storage in the vector database."""
    return [embed_text(t, task_type="RETRIEVAL_DOCUMENT") for t in texts]


def embed_query(text: str) -> list[float]:
    """Embed a single live user question for similarity search."""
    return embed_text(text, task_type="RETRIEVAL_QUERY")
