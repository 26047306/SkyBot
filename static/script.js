let recognition;
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");

// 🎙️ Mic Input Setup
if ("webkitSpeechRecognition" in window) {
  recognition = new webkitSpeechRecognition();
  recognition.lang = "hi-IN";
  recognition.continuous = false;
  recognition.interimResults = false;

  micBtn.addEventListener("click", () => {
    recognition.start();
  });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
  };

  recognition.onerror = (event) => {
    alert("Mic Error: " + event.error);
  };
} else {
  micBtn.disabled = true;
  micBtn.title = "Speech Recognition not supported";
}

// 📤 Send message on button click
sendBtn.addEventListener("click", sendMessage);

// ✅ Define sendMessage function
function sendMessage() {
  const message = userInput.value.trim();
  if (message === "") return;

  addMessage("user", message);
  userInput.value = "";
  sendMessageToBot(message);
}

// ➕ Show message in chat
function addMessage(sender, text) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.textContent = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// 📡 Call Flask API
async function sendMessageToBot(message) {
  addMessage("bot", "Typing...");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await res.json();
    const botMessages = chatBox.getElementsByClassName("bot");
    const lastBotMsg = botMessages[botMessages.length - 1];

    typeEffect(lastBotMsg, data.response);
  } catch (err) {
    console.error("Error:", err);
    addMessage("bot", "Something went wrong! Please try again.");
  }
}

// ⌨️ Typing effect
function typeEffect(element, text, i = 0) {
  if (i < text.length) {
    element.textContent = text.substring(0, i + 1);
    setTimeout(() => typeEffect(element, text, i + 1), 20);
  }
}
