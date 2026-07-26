"""
app.py
------
The UI layer. Deliberately thin — all the real logic lives in
chat_engine.py, vector_store.py, and tools.py. This file's only job is
to wire the chat function into Gradio and launch it.

Run: python app.py
(Make sure you've run build_index.py at least once first!)
"""

import os
import gradio as gr
from chat_engine import chat
from vector_store import ensure_index_built

if __name__ == "__main__":
    ensure_index_built()
    port = int(os.environ.get("PORT", 7860))
    gr.ChatInterface(chat).launch(server_name="0.0.0.0", server_port=port)
