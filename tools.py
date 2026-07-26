"""
tools.py
--------
Everything related to "side effects" the chatbot can trigger: Pushover
notifications, and the tool schemas + dispatcher that let Gemini call
Python functions mid-conversation.
"""

import json
import requests

from config import PUSHOVER_TOKEN, PUSHOVER_USER

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"


def push(message: str):
    print(f"[Pushover] Sending: {message}")
    requests.post(
        PUSHOVER_URL,
        data={"token": PUSHOVER_TOKEN, "user": PUSHOVER_USER, "message": message},
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"New lead captured!\nName: {name}\nEmail: {email}\nNotes: {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question):
    push(f"Bot couldn't answer a question: {question}")
    return {"recorded": "ok"}


record_user_details_json = {
    "name": "record_user_details",
    "description": "Record that a user is interested in being in touch and provided an email",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of the user"},
            "name": {"type": "string", "description": "The user's name, if provided"},
            "notes": {"type": "string", "description": "Additional context worth noting"},
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Record any question that couldn't be answered from the provided context",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

_FUNCTION_REGISTRY = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
}


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}({arguments})", flush=True)

        tool_function = _FUNCTION_REGISTRY.get(tool_name)
        result = tool_function(**arguments) if tool_function else {}

        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    return results
