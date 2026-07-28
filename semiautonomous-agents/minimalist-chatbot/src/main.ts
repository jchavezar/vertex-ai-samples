// main.ts - Premium Minimalist Chatbot Frontend

// Interfaces
interface ChatEvent {
  type: "text" | "thought" | "tool_call" | "tool_result" | "usage" | "error" | "done";
  text?: string;
  thought?: string;
  tool?: { name: string; args: any };
  result?: { name: string; response: any };
  error?: string;
}

// State variables
let sessionId: string | null = sessionStorage.getItem("aura_session_id");
const userId = "jesus-user";
const BACKEND_URL = "http://localhost:8001";
let isStreaming = false;

// DOM Elements
const backendStatus = document.getElementById("backend-status") as HTMLSpanElement;
const statusDot = document.querySelector(".status-dot") as HTMLSpanElement;
const messagesContainer = document.getElementById("messages-container") as HTMLSectionElement;
const welcomeScreen = document.getElementById("welcome-screen") as HTMLDivElement;
const chatForm = document.getElementById("chat-form") as HTMLFormElement;
const chatInput = document.getElementById("chat-input") as HTMLTextAreaElement;
const sendButton = document.getElementById("send-button") as HTMLButtonElement;
const toolActivityBanner = document.getElementById("tool-activity-banner") as HTMLDivElement;
const toolActivityText = document.getElementById("tool-activity-text") as HTMLSpanElement;

// Lightweight regex markdown-to-HTML parser for premium formatting (including citations)
function parseMarkdown(text: string): string {
  if (!text) return "";
  
  let html = text;
  
  // Escape HTML tags to prevent XSS
  html = html
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Bold (**text**)
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  
  // Italic (*text*)
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  
  // Inline Code (`code`)
  html = html.replace(/`(.*?)`/g, "<code>$1</code>");
  
  // Clickable Citations / Links [title](url)
  // Ensures links open in a new tab securely
  html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  // Multi-line formatting: Paragraphs and lists
  const lines = html.split("\n");
  let inList = false;
  let formattedHtml = "";

  for (let line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (!inList) {
        formattedHtml += "<ul>";
        inList = true;
      }
      formattedHtml += `<li>${trimmed.substring(2)}</li>`;
    } else {
      if (inList) {
        formattedHtml += "</ul>";
        inList = false;
      }
      if (trimmed) {
        formattedHtml += `<p>${line}</p>`;
      } else {
        formattedHtml += "<br/>";
      }
    }
  }
  
  if (inList) {
    formattedHtml += "</ul>";
  }

  // Clean double brs
  return formattedHtml.replace(/(<br\/>)+/g, "<br/>");
}

// Auto scroll to bottom
function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Set up UI health status
async function checkBackendHealth() {
  backendStatus.textContent = "Connecting...";
  statusDot.className = "status-dot connecting";
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`);
    if (response.ok) {
      backendStatus.textContent = "Aura Engine Online";
      statusDot.className = "status-dot healthy";
      sendButton.disabled = false;
      return true;
    }
  } catch (error) {
    console.error("Backend offline:", error);
  }
  
  backendStatus.textContent = "Aura Engine Offline";
  statusDot.className = "status-dot error";
  sendButton.disabled = true;
  return false;
}

// Initialize Chat Session
async function initSession() {
  const isHealthy = await checkBackendHealth();
  if (!isHealthy) return;

  if (sessionId) {
    console.log(`>>> [Session] Resuming active session: ${sessionId}`);
    return;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId })
    });
    
    if (response.ok) {
      const data = await response.json();
      sessionId = data.session_id;
      if (sessionId) {
        sessionStorage.setItem("aura_session_id", sessionId);
        console.log(`>>> [Session] Session initialized successfully: ${sessionId}`);
      }
    }
  } catch (err) {
    console.error(">>> [Session Error] Failed to fetch session:", err);
  }
}

// Resize textarea dynamically based on content
function adjustInputHeight() {
  chatInput.style.height = "auto";
  chatInput.style.height = `${chatInput.scrollHeight}px`;
}

// Display user message in chat window
function appendUserMessage(text: string) {
  if (welcomeScreen) {
    welcomeScreen.style.display = "none";
  }

  const row = document.createElement("div");
  row.className = "message-row user";
  
  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = text;
  
  row.appendChild(bubble);
  messagesContainer.appendChild(row);
  scrollToBottom();
}

// Tool activity banner helper
function showToolActivity(text: string) {
  toolActivityText.textContent = text;
  toolActivityBanner.classList.remove("hidden");
}

function hideToolActivity() {
  toolActivityBanner.classList.add("hidden");
}

// Send message and stream the response
async function sendMessage(messageText: string) {
  if (isStreaming) return;
  
  // Double check session ID
  if (!sessionId) {
    await initSession();
    if (!sessionId) {
      alert("Could not initialize chat session. Ensure your backend is running.");
      return;
    }
  }

  appendUserMessage(messageText);
  isStreaming = true;
  sendButton.disabled = true;

  // Append assistant message row & structure
  const row = document.createElement("div");
  row.className = "message-row assistant";
  
  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  
  // Thought area container (rendered if thoughts stream in)
  const thoughtArea = document.createElement("div");
  thoughtArea.className = "thought-block";
  thoughtArea.style.display = "none";
  
  // Content text element
  const contentArea = document.createElement("div");
  contentArea.className = "content-area";
  // Add a premium flashing cursor indicator on streamstart
  contentArea.innerHTML = '<span class="activity-spinner" style="display:inline-block; vertical-align:middle;"></span>';
  
  bubble.appendChild(thoughtArea);
  bubble.appendChild(contentArea);
  row.appendChild(bubble);
  messagesContainer.appendChild(row);
  scrollToBottom();

  let accumulatedText = "";
  let accumulatedThought = "";

  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: messageText,
        session_id: sessionId,
        user_id: userId
      })
    });

    if (!response.ok) {
      throw new Error(`API Connection Failed (${response.status})`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("No readable body on response.");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // hold incomplete line

      for (const line of lines) {
        if (!line.trim()) continue;
        if (!line.startsWith("data:")) continue;

        const dataStr = line.substring(5).trim();
        if (!dataStr) continue;

        try {
          const event = JSON.parse(dataStr) as ChatEvent;
          
          if (event.type === "text" && event.text) {
            // Remove spinner placeholder on first content chunk
            if (contentArea.querySelector(".activity-spinner")) {
              contentArea.innerHTML = "";
            }
            accumulatedText += event.text;
            contentArea.innerHTML = parseMarkdown(accumulatedText);
            scrollToBottom();
          } 
          
          else if (event.type === "thought" && event.thought) {
            thoughtArea.style.display = "block";
            accumulatedThought += event.thought;
            thoughtArea.textContent = `Thought process:\n${accumulatedThought}`;
            scrollToBottom();
          } 
          
          else if (event.type === "tool_call" && event.tool) {
            showToolActivity(`Aura calling: ${event.tool.name}...`);
          } 
          
          else if (event.type === "tool_result" && event.result) {
            showToolActivity(`Success: ${event.result.name} executed.`);
            setTimeout(hideToolActivity, 2500);
          } 
          
          else if (event.type === "error" && event.error) {
            contentArea.innerHTML += `<div style="color: #ef4444; margin-top: 10px;">[Error: ${event.error}]</div>`;
            scrollToBottom();
          }
        } catch (e) {
          // Keep parsing
        }
      }
    }
  } catch (error: any) {
    console.error("Streaming error:", error);
    contentArea.innerHTML = `<span style="color: #ef4444;">Could not connect to back engine stream. Ensure your local server is up and authenticated. (${error.message})</span>`;
  } finally {
    isStreaming = false;
    sendButton.disabled = false;
    hideToolActivity();
    
    // Clear initial spinner if stream completed empty
    if (contentArea.querySelector(".activity-spinner")) {
      contentArea.innerHTML = "No response content received.";
    }
    
    chatInput.focus();
  }
}

// Event Listeners
chatInput.addEventListener("input", () => {
  adjustInputHeight();
  sendButton.disabled = isStreaming || !chatInput.value.trim();
});

chatInput.addEventListener("keydown", (e: KeyboardEvent) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.dispatchEvent(new Event("submit"));
  }
});

chatForm.addEventListener("submit", (e: Event) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text || isStreaming) return;
  
  chatInput.value = "";
  chatInput.style.height = "auto"; // reset input height
  sendMessage(text);
});

// Prompt cards triggers
document.querySelectorAll(".prompt-card").forEach(card => {
  card.addEventListener("click", () => {
    const prompt = card.getAttribute("data-prompt");
    if (prompt && !isStreaming) {
      sendMessage(prompt);
    }
  });
});

// Initial load
window.addEventListener("DOMContentLoaded", () => {
  initSession();
  
  // Re-check health every 15s to keep UI updated
  setInterval(checkBackendHealth, 15000);
});
