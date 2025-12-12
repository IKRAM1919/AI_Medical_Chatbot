const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const typingBubble = document.getElementById("typing");

function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.textContent = text;
    chatBox.appendChild(msg);
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, "user");
    userInput.value = "";
    sendBtn.disabled = true;
    typingBubble.classList.remove("hidden");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: text }),
        });
        const data = await response.json();
        setTimeout(() => {
            addMessage(data.answer, "bot");
            typingBubble.classList.add("hidden");
            sendBtn.disabled = false;
        }, 800);
    } catch (error) {
        addMessage("⚠️ Error connecting to server.", "bot");
        typingBubble.classList.add("hidden");
        sendBtn.disabled = false;
        console.error("Chat API error:", error);
    }
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
});
