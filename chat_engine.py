"""
chat_engine.py
--------------
The core conversational logic, kept separate from the UI (app.py) so it
could be reused with a different frontend later (e.g. a web API instead
of Gradio) without touching this file.

Per turn:
  1. Retrieve relevant chunks from the vector store (vector_store.py)
  2. Build a system prompt with that context injected
  3. Run the tool-calling loop against Gemini (tools.py)
"""

from openai import OpenAI

from config import GEMINI_API_KEY, CHAT_MODEL
from vector_store import retrieve
from tools import tools, handle_tool_calls

gemini_client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

SYSTEM_PROMPT_TEMPLATE = """You are a helpful assistant on Kalyani's portfolio website,
chatting with a visitor (recruiter, hiring manager, or potential client).
Be professional, friendly, and engaging.

Use ONLY the context below to answer questions about Kalyani. If the answer isn't
in the context, use the record_unknown_question tool to log it instead of guessing.
If the visitor seems interested in continuing the conversation, politely ask for
their email and use the record_user_details tool to log it.

Context retrieved for this question:
{context}
"""


def chat(message: str, history: list[dict]) -> str:
    relevant_chunks = retrieve(message)
    context = "\n\n".join(relevant_chunks) if relevant_chunks else "No relevant context found."
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)

    messages = (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": message}]
    )

    done = False
    response = None
    while not done:
        response = gemini_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            tools=tools,
        )
        finish_reason = response.choices[0].finish_reason

        if finish_reason == "tool_calls":
            reply_message = response.choices[0].message
            tool_calls = reply_message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(reply_message)
            messages.extend(results)
        else:
            done = True

    return response.choices[0].message.content
