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

function getOfflineChatbotReply(message) {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('flood') || lowerMessage.includes('flooding') || 
        lowerMessage.includes('बाढ़') || 
        lowerMessage.includes('inundación') || lowerMessage.includes('inundacion') || 
        lowerMessage.includes('inondation')) {
        return typeof i18next !== 'undefined' ? i18next.t("bot_reply_flood") : "🌊 Flood safety: move to higher ground, avoid walking or driving through floodwater, keep emergency supplies ready, and follow local evacuation updates.";
    }

    if (lowerMessage.includes('heatwave') || lowerMessage.includes('heat') || lowerMessage.includes('extreme heat') ||
        lowerMessage.includes('गर्मी') || lowerMessage.includes('लू') || 
        lowerMessage.includes('calor') || 
        lowerMessage.includes('chaleur') || lowerMessage.includes('canicule')) {
        return typeof i18next !== 'undefined' ? i18next.t("bot_reply_heat") : "🔥 Heatwave safety: drink water often, avoid direct afternoon sun, wear light clothing, check on vulnerable people, and seek cooling support if you feel dizzy or weak.";
    }

    if (lowerMessage.includes('cyclone') || lowerMessage.includes('hurricane') || lowerMessage.includes('typhoon') ||
        lowerMessage.includes('चक्रवात') || 
        lowerMessage.includes('ciclón') || lowerMessage.includes('ciclon') || 
        lowerMessage.includes('cyclone')) {
        return typeof i18next !== 'undefined' ? i18next.t("bot_reply_cyclone") : "🌀 Cyclone safety: secure loose outdoor items, charge devices, keep documents and medicines ready, stay away from windows, and follow official shelter guidance.";
    }

    if (lowerMessage.includes('wildfire') || lowerMessage.includes('fire') ||
        lowerMessage.includes('आग') || 
        lowerMessage.includes('incendio') || 
        lowerMessage.includes('incendie')) {
        return typeof i18next !== 'undefined' ? i18next.t("bot_reply_wildfire") : "🌲 Wildfire safety: monitor evacuation alerts, reduce smoke exposure, keep masks and medicines ready, close windows, and leave early if officials warn your area.";
    }

    if (lowerMessage.includes('climate change') || lowerMessage.includes('climate') ||
        lowerMessage.includes('जलवायु') || 
        lowerMessage.includes('clima') || 
        lowerMessage.includes('climat')) {
        return typeof i18next !== 'undefined' ? i18next.t("bot_reply_climate") : "🌎 Climate change can intensify heavy rainfall, heatwaves, drought, and storms. Preparedness, early warnings, and resilient local planning reduce risk.";
    }

    return typeof i18next !== 'undefined' ? i18next.t("bot_reply_default") : "💡 I can help with flood safety, heatwaves, cyclones, wildfire preparedness, and climate risk basics. Try asking for safety tips for one hazard.";
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

    function renderSuggestionChips() {
        suggestionContainer.innerHTML = '';
        
        const suggestions = [
            { 
                label: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_flood_lbl") : "🌊 Flood Safety", 
                text: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_flood_txt") : "what precautions should i take during floods?" 
            },
            { 
                label: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_heat_lbl") : "🔥 Heatwave Safety", 
                text: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_heat_txt") : "what precautions should i take during heatwaves?" 
            },
            { 
                label: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_wildfire_lbl") : "🌲 Wildfire Safety", 
                text: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_wildfire_txt") : "what precautions should i take during wildfires?" 
            },
            { 
                label: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_cyclone_lbl") : "🌀 Cyclone Safety", 
                text: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_cyclone_txt") : "what precautions should i take during cyclones?" 
            },
            { 
                label: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_summary_lbl") : "📊 Risk Summary Here", 
                text: typeof i18next !== 'undefined' ? i18next.t("bot_suggest_summary_txt") : "what is the current risk summary here?" 
            }
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
    }

    renderSuggestionChips();

    // Inject chips above the typing form
    panel.insertBefore(suggestionContainer, form);

    window.addEventListener('languagechange', () => {
        renderSuggestionChips();
    });

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
        const errMsg = typeof i18next !== 'undefined' ? i18next.t("bot_err_empty") : "⚠️ Please enter a message.";

        // Duplicate message check
        const lastMsg = messages.lastChild;
        if (!message && lastMsg && lastMsg.textContent === errMsg) {
            return;
        }

        if (!message) {
            appendChatMessage(messages, errMsg, "bot", true);
            return;
        }

        appendChatMessage(messages, message, 'user', true);
        input.value = '';

        setChatStatus(status, typeof i18next !== 'undefined' ? i18next.t("bot_status_thinking") : 'ClimateBot is thinking...');

        // Local Context Interception
        const lowerMsg = message.toLowerCase();
        const activeReport = window.activeClimateReport;
        
        const localKeywords = [
            "here", "current", "this", "summary",
            "यहाँ", "वर्तमान", "इस", "सारांश",
            "aquí", "aqui", "actual", "este", "esta", "resumen",
            "ici", "actuel", "ce", "cet", "cette", "résumé", "resume"
        ];
        const matchesLocalKeyword = localKeywords.some(kw => lowerMsg.includes(kw));
        const matchesCity = activeReport && lowerMsg.includes(activeReport.location.city.toLowerCase());

        if (activeReport && (matchesLocalKeyword || matchesCity)) {
            // Serve dynamic, context-aware answers instantly on the client side!
            setTimeout(() => {
                const city = activeReport.location.city;
                const temp = activeReport.weather.temperature;
                const humid = activeReport.weather.humidity;
                const rain = activeReport.weather.rainfall;
                const wind = activeReport.weather.wind_speed;
                const fRisk = activeReport.risks.flood_risk;
                const hRisk = activeReport.risks.heat_risk;
                const wRisk = activeReport.risks.wildfire_risk;
                const cRisk = activeReport.risks.cyclone_risk;
                const dRisk = activeReport.risks.drought_risk;
                
                let responseText = "";
                if (typeof i18next !== 'undefined') {
                    responseText = i18next.t("bot_context_reply", {
                        city, temp, humid, rain, wind, fRisk, hRisk, wRisk, cRisk, dRisk
                    });
                }
                
                if (!responseText || responseText === "bot_context_reply") {
                    responseText = `Here is the current weather & risk summary for ${city}:\n\n`;
                    responseText += `🌡️ Temp: ${temp} °C | 💧 Humid: ${humid}%\n`;
                    responseText += `🌧️ Rain: ${rain} mm | 🌪️ Wind: ${wind} km/h\n\n`;
                    responseText += `⚠️ Hazard Risk Ratings (Scale 0-1.0):\n`;
                    responseText += `- Flood Risk: ${fRisk} (Threshold: 0.65)\n`;
                    responseText += `- Heat Risk: ${hRisk} (Threshold: 0.75)\n`;
                    responseText += `- Wildfire Risk: ${wRisk} (Threshold: 0.65)\n`;
                    responseText += `- Cyclone Risk: ${cRisk} (Threshold: 0.60)\n`;
                    responseText += `- Drought Risk: ${dRisk} (Threshold: 0.70)\n\n`;
                    responseText += `📢 Current Advisory Alert:\n`;
                    responseText += activeReport.alerts.map(a => `${a}`).join('\n');
                } else {
                    const alertTitle = i18next.t("bot_context_advisory_title");
                    responseText += `\n\n📢 ${alertTitle}:\n` + activeReport.alerts.map(a => `${a}`).join('\n');
                }
                
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
                body: JSON.stringify({
                    message,
                    context: window.lastAnalysisContext || null,
                    lang: typeof i18next !== 'undefined' ? i18next.language : 'en'
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                appendChatMessage(
                    messages,
                    data.message || (typeof i18next !== 'undefined' ? i18next.t("err_chatbot_unavailable") : 'Unable to get a chatbot response right now.'),
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
                getOfflineChatbotReply(message),
                'bot',
                true
            );
            setChatStatus(status, '');
        }
    });
});
