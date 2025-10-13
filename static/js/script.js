document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    let conversationHistory = [];

    // --- Function to add a message to the chat display ---
    const addMessage = (sender, message) => {
        const messageElement = document.createElement("div");
        messageElement.classList.add(
            "chat-message",
            sender === "user" ? "user-message" : "bot-message"
        );
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message
    };

    // --- Greet the user on page load ---
    const initialBotMessage =
        "Hello! I'm your AI Product Assistant. How can I help you with your business requirements today?";
    addMessage("bot", initialBotMessage);
    conversationHistory.push({ role: "assistant", content: initialBotMessage });

    // --- Function to handle sending a message ---
    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage("user", message);
        userInput.value = "";

        // Add user message to conversation history
        conversationHistory.push({ role: "user", content: message });

        try {
            // --- API Call to the Backend ---
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: message,
                    history: conversationHistory,
                }),
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await response.json();
            addMessage("bot", data.response);

            // Add bot response to conversation history
            conversationHistory.push({
                role: "assistant",
                content: data.response,
            });
        } catch (error) {
            console.error("Error:", error);
            addMessage("bot", "Sorry, something went wrong. Please try again.");
        }
    };

    // --- Event Listeners ---
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});
