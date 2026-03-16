// ============================================================
//   RuleBot — Chat Frontend Logic
// ============================================================

let msgCount  = 0;
let isWaiting = false;

// ── DOM refs ─────────────────────────────────────────────────
const messagesEl  = document.getElementById("messages");
const inputEl     = document.getElementById("userInput");
const sendBtn     = document.getElementById("sendBtn");
const msgCountEl  = document.getElementById("msgCount");
const typingEl    = document.getElementById("typingIndicator");
const charCountEl = document.getElementById("charCount");

// ── Init ─────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  inputEl.focus();
  updateMsgCount();
});

// ── Key handler ───────────────────────────────────────────────
function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }

  // Show char count when typing
  const len = inputEl.value.length;
  if (len > 300) {
    charCountEl.style.display = "block";
    charCountEl.textContent   = `${len}/500`;
    charCountEl.style.color   = len > 450 ? "#ef4444" : "var(--muted)";
  } else {
    charCountEl.style.display = "none";
  }
}

// ── Send message ──────────────────────────────────────────────
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || isWaiting) return;

  inputEl.value = "";
  charCountEl.style.display = "none";
  isWaiting = true;
  sendBtn.disabled = true;

  // Render user message
  appendMessage("user", text);

  // Show typing indicator
  showTyping();

  // Calculate realistic delay (50–120ms per char, capped)
  const delay = Math.min(400 + text.length * 15, 1600);

  try {
    const resp = await fetch("/api/chat", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message: text }),
    });

    const data = await resp.json();

    setTimeout(() => {
      hideTyping();
      if (data.reply) {
        appendMessage("bot", data.reply, data.timestamp);
        if (data.session) {
          document.getElementById("sessionId").textContent = data.session;
        }
      } else {
        appendMessage("bot", "⚠️ Something went wrong. Try again!");
      }
      isWaiting    = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }, delay);

  } catch (err) {
    setTimeout(() => {
      hideTyping();
      appendMessage("bot", "⚠️ Network error. Is the Flask server running?");
      isWaiting    = false;
      sendBtn.disabled = false;
    }, 400);
  }
}

// ── Suggestion chip ───────────────────────────────────────────
function sendSuggestion(btn) {
  // Strip emoji prefix for cleaner input
  const raw  = btn.textContent.trim();
  const text = raw.replace(/[\u{1F300}-\u{1FFFF}]/gu, "").replace(/[⏰📅🆘🤖👋😄]/gu, "").trim();
  inputEl.value = text || raw;
  sendMessage();
}

// ── Append message bubble ─────────────────────────────────────
function appendMessage(role, text, timestamp) {
  const now   = timestamp || new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const isBot = role === "bot";

  const row = document.createElement("div");
  row.className = `msg-row ${role}`;

  // Format text — handle newlines, bold (**text**), inline code (`text`)
  const formatted = formatText(text);

  row.innerHTML = `
    <div class="msg-avatar">${isBot ? "🤖" : "🙂"}</div>
    <div class="msg-bubble ${role}">
      <div class="msg-text">${formatted}</div>
      <div class="msg-meta">${isBot ? "RuleBot" : "You"} · ${now}</div>
    </div>
  `;

  messagesEl.appendChild(row);
  msgCount++;
  updateMsgCount();
  scrollToBottom();

  // Flash input on bot reply
  if (isBot) {
    document.querySelector(".input-wrap").classList.add("flash");
    setTimeout(() => document.querySelector(".input-wrap").classList.remove("flash"), 400);
  }
}

// ── Text formatting ───────────────────────────────────────────
function formatText(text) {
  // Escape HTML
  let t = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Newlines → <br>
  t = t.replace(/\n/g, "<br>");

  // **bold** → <strong>
  t = t.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // `code` → <code>
  t = t.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Highlight math result numbers after =
  t = t.replace(/= <strong>(.+?)<\/strong>/g, '= <span class="math-result">$1</span>');

  return t;
}

// ── Typing indicator ──────────────────────────────────────────
let typingRow = null;

function showTyping() {
  typingEl.style.display = "flex";

  typingRow = document.createElement("div");
  typingRow.className = "msg-row bot typing-msg";
  typingRow.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div class="msg-bubble bot">
      <div class="msg-text">
        <div class="typing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
  `;
  messagesEl.appendChild(typingRow);
  scrollToBottom();
}

function hideTyping() {
  typingEl.style.display = "none";
  if (typingRow) {
    typingRow.remove();
    typingRow = null;
  }
}

// ── Clear chat ────────────────────────────────────────────────
async function clearChat() {
  try {
    await fetch("/api/clear", { method: "POST" });
  } catch {}

  messagesEl.innerHTML = "";
  msgCount = 0;
  updateMsgCount();
  isWaiting = false;
  sendBtn.disabled = false;
  hideTyping();

  // Re-add welcome
  setTimeout(() => {
    appendMessage(
      "bot",
      "Chat cleared! 🗑️\n\nHello again! 👋 How can I help you? Type **help** to see what I can do.",
    );
  }, 100);
}

// ── Helpers ───────────────────────────────────────────────────
function updateMsgCount() {
  msgCountEl.textContent = `${msgCount} message${msgCount !== 1 ? "s" : ""}`;
}

function scrollToBottom() {
  const wrap = document.getElementById("messagesWrap");
  wrap.scrollTop = wrap.scrollHeight;
}
