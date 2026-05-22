const CHATBOT_API_URL =
    window.location.origin + '/chatbot';

function appendChatMessage(container, text, role) {
    const message = document.createElement('div');
    message.className = `chatbot-message ${role}-message`;
    message.textContent = text;
    container.appendChild(message);
    container.scrollTop = container.scrollHeight;
}

function setChatStatus(statusElement, text) {
    if (!text) {
        statusElement.textContent = '';
        statusElement.classList.add('hidden');
        return;
    }

    statusElement.textContent = text;
    statusElement.classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    const panel = document.getElementById('chatbot-panel');
    const toggleButton = document.getElementById('chatbot-toggle');
    const closeButton = document.getElementById('chatbot-close');
    const form = document.getElementById('chatbot-form');
    const input = document.getElementById('chatbot-input');
    const messages = document.getElementById('chatbot-messages');
    const status = document.getElementById('chatbot-status');

    if (!panel || !toggleButton || !closeButton || !form || !input || !messages || !status) {
        return;
    }

    const openPanel = () => {
        panel.classList.remove('hidden');
        toggleButton.setAttribute('aria-expanded', 'true');
        input.focus();
    };

    const closePanel = () => {
        panel.classList.add('hidden');
        toggleButton.setAttribute('aria-expanded', 'false');
    };

    toggleButton.addEventListener('click', () => {
        if (panel.classList.contains('hidden')) {
            openPanel();
            return;
        }
        closePanel();
    });

    closeButton.addEventListener('click', closePanel);

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const message = input.value.trim();
        if (!message) {
            return;
        }

        appendChatMessage(messages, message, 'user');
        input.value = '';
        setChatStatus(status, 'ClimateBot is thinking...');

        try {
            const response = await fetch(CHATBOT_API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                appendChatMessage(messages, data.message || 'Unable to get a chatbot response right now.', 'bot');
                setChatStatus(status, '');
                return;
            }

            appendChatMessage(messages, data.response, 'bot');
            setChatStatus(status, '');
        } catch (error) {
            console.error(error);
            appendChatMessage(messages, 'Chatbot backend is not running. Start chatbot.py in API mode.', 'bot');
            setChatStatus(status, '');
        }
    });
});
