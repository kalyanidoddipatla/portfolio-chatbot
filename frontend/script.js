// script.js
// Handles: opening/closing the floating widget, sending messages to the
// FastAPI backend, rendering log-style entries, and keeping conversation
// history in the same {role, content} shape chat_engine.py expects.

const widgetRoot = document.getElementById("widget-root");
const toggleBtn = document.getElementById("widget-toggle");
const log = document.getElementById("log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");

let history = [];
let hasOpenedOnce = false;

toggleBtn.addEventListener("click", () => {
  const isOpen = widgetRoot.classList.toggle("open");
  if (isOpen && !hasOpenedOnce) {
    hasOpenedOnce = true;
    input.focus();
  }
});

function timestamp() {
  const now = new Date();
  return now.toLocaleTimeString("en-GB", { hour12: false });
}

function addEntry(role, text) {
  const entry = document.createElement("div");
  entry.className = `entry entry-${role}`;

  const meta = document.createElement("span");
  meta.className = "entry-meta";
  const label = role === "user" ? "you" : role === "assistant" ? "assistant" : "system";
  meta.textContent = `[${timestamp()}] ${label}`;

  const textEl = document.createElement("span");
  textEl.className = "entry-text";
  textEl.textContent = text;

  entry.appendChild(meta);
  entry.appendChild(textEl);
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
  return entry;
}

async function sendMessage(message) {
  addEntry("user", message);
  history.push({ role: "user", content: message });

  const pending = addEntry("assistant", "...");
  pending.classList.add("entry-pending");

  sendBtn.disabled = true;
  input.disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history: history.slice(0, -1) }),
    });

    if (!response.ok) throw new Error(`Server responded ${response.status}`);

    const data = await response.json();
    pending.querySelector(".entry-text").textContent = data.reply;
    pending.classList.remove("entry-pending");
    history.push({ role: "assistant", content: data.reply });
  } catch (err) {
    pending.querySelector(".entry-text").textContent =
      "Something went wrong reaching the assistant. Please try again.";
    pending.classList.remove("entry-pending");
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  sendMessage(message);
});
