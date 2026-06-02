const CHATBOT_API_URL =
    window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
        ? "http://127.0.0.1:5000/chatbot"
        : window.location.origin + "/chatbot";

// ==========================================
// FIX FOR ISSUE #85: Global Tracking Utility
// ==========================================
let globalChatHistory = [];

function appendChatMessage(container, text, role, shouldSave = true) {
    const message = document.createElement('div');
    message.className = `chatbot-message ${role}-message`;
    message.textContent = text;
    message.style.whiteSpace = 'pre-wrap'; // Preserve newlines and lists
    container.appendChild(message);
    container.scrollTop = container.scrollHeight;

    // Save message context to state history and push to localStorage
    if (shouldSave) {
        globalChatHistory.push({ text, role });
        try {
            localStorage.setItem('climate_chatbot_history', JSON.stringify(globalChatHistory));
        } catch (e) {
            console.error("Failed to write message to localStorage:", e);
        }
    }
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

    // ==========================================
    // FIX FOR ISSUE #85: Restore Chat History on Startup
    // ==========================================
    try {
        const savedHistory = localStorage.getItem('climate_chatbot_history');
        if (savedHistory) {
            globalChatHistory = JSON.parse(savedHistory);
            globalChatHistory.forEach(msg => {
                // Pass false so it prints to the screen without creating duplicates inside the array
                appendChatMessage(messages, msg.text, msg.role, false);
            });
        }
    } catch (error) {
        console.error("Failed to recover message arrays from storage tracking:", error);
    }

    // Dynamic Suggestion Chips Injection
    const suggestionContainer = document.createElement('div');
    suggestionContainer.id = 'chatbot-suggestions';
    suggestionContainer.style.display = 'flex';
    suggestionContainer.style.flexWrap = 'wrap';
    suggestionContainer.style.gap = '6px';
    suggestionContainer.style.marginBottom = '10px';
    suggestionContainer.style.padding = '4px 2px';

    const suggestions = [
        { label: "🌊 Flood Safety", text: "what precautions should i take during floods?" },
        { label: "🔥 Heatwave Safety", text: "what precautions should i take during heatwaves?" },
        { label: "🌲 Wildfire Safety", text: "what precautions should i take during wildfires?" },
        { label: "🌀 Cyclone Safety", text: "what precautions should i take during cyclones?" },
        { label: "📊 Risk Summary Here", text: "what is the current risk summary here?" }
    ];

    suggestions.forEach(item => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.textContent = item.label;
        chip.style.background = 'rgba(255, 255, 255, 0.08)';
        chip.style.border = '1px solid rgba(255, 255, 255, 0.12)';
        chip.style.color = '#cbd5e1';
        chip.style.borderRadius = '20px';
        chip.style.padding = '5px 10px';
        chip.style.fontSize = '0.74rem';
        chip.style.cursor = 'pointer';
        chip.style.transition = 'background-color 0.2s, color 0.2s';
        chip.style.fontFamily = 'inherit';

        chip.addEventListener('mouseenter', () => {
            chip.style.background = 'rgba(56, 189, 248, 0.15)';
            chip.style.color = '#fff';
            chip.style.borderColor = 'rgba(56, 189, 248, 0.3)';
        });
        chip.addEventListener('mouseleave', () => {
            chip.style.background = 'rgba(255, 255, 255, 0.08)';
            chip.style.color = '#cbd5e1';
            chip.style.borderColor = 'rgba(255, 255, 255, 0.12)';
        });

        chip.addEventListener('click', () => {
            input.value = item.text;
            form.dispatchEvent(new Event('submit'));
        });

        suggestionContainer.appendChild(chip);
    });

    // Inject chips above the typing form
    panel.insertBefore(suggestionContainer, form);

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

        appendChatMessage(messages, message, 'user', true);
        input.value = '';

        setChatStatus(status, 'ClimateBot is thinking...');

        // Local Context Interception
        const lowerMsg = message.toLowerCase();
        const activeReport = window.activeClimateReport;
        
        if (activeReport && (
            lowerMsg.includes("here") || 
            lowerMsg.includes("current") || 
            lowerMsg.includes("this") || 
            lowerMsg.includes("summary") || 
            lowerMsg.includes(activeReport.location.city.toLowerCase())
        )) {
            // Serve dynamic, context-aware answers instantly on the client side!
            setTimeout(() => {
                let responseText = `Here is the current weather & risk summary for ${activeReport.location.city}:\n\n`;
                responseText += `🌡️ Temp: ${activeReport.weather.temperature} °C | 💧 Humid: ${activeReport.weather.humidity}%\n`;
                responseText += `🌧️ Rain: ${activeReport.weather.rainfall} mm | 🌪️ Wind: ${activeReport.weather.wind_speed} km/h\n\n`;
                responseText += `⚠️ Hazard Risk Ratings (Scale 0-1.0):\n`;
                responseText += `- Flood Risk: ${activeReport.risks.flood_risk} (Threshold: 0.65)\n`;
                responseText += `- Heat Risk: ${activeReport.risks.heat_risk} (Threshold: 0.75)\n`;
                responseText += `- Wildfire Risk: ${activeReport.risks.wildfire_risk} (Threshold: 0.65)\n`;
                responseText += `- Cyclone Risk: ${activeReport.risks.cyclone_risk} (Threshold: 0.60)\n`;
                responseText += `- Drought Risk: ${activeReport.risks.drought_risk} (Threshold: 0.70)\n\n`;
                responseText += `📢 Current Advisory Alert:\n`;
                responseText += activeReport.alerts.map(a => `${a}`).join('\n');
                
                appendChatMessage(messages, responseText, 'bot', true);
                setChatStatus(status, '');
            }, 550);
            return;
        }

        try {
            const response = await fetch(CHATBOT_API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                appendChatMessage(
                    messages,
                    data.message || 'Unable to get a chatbot response right now.',
                    'bot',
                    true
                );
                setChatStatus(status, '');
                return;
            }

            appendChatMessage(messages, data.response, 'bot', true);
            setChatStatus(status, '');

        } catch (error) {
            console.error(error);
            appendChatMessage(
                messages,
                'Chatbot backend is not running.',
                'bot',
                true
            );
            setChatStatus(status, '');
        }
    });
});
