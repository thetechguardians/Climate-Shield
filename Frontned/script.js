document.addEventListener('DOMContentLoaded', () => {
            // --- 1. INITIALIZE MAP ---
            const map = L.map('map', { zoomControl: false }).setView([20, 0], 3);

            // CHANGED: Using a light theme for the map tiles
            L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(map);

            L.control.zoom({ position: 'topright' }).addTo(map);

            const markers = {};
            let alerts = [];

            // Allowed Severity levels
            const severities = [
                { level: 'Critical', bgClass: 'bg-severity-critical/20', textClass: 'text-severity-critical', borderClass: 'border-severity-critical/30', colorHex: '#ef4444' },
                { level: 'High', bgClass: 'bg-severity-high/20', textClass: 'text-severity-high', borderClass: 'border-severity-high/30', colorHex: '#f97316' },
                { level: 'Medium', bgClass: 'bg-severity-medium/20', textClass: 'text-severity-medium', borderClass: 'border-severity-medium/30', colorHex: '#eab308' }
            ];

            // Focused Event Types
            const eventTypes = [
                { type: 'Flood Warning', icon: 'fa-water' },
                { type: 'Heatwave Alert', icon: 'fa-temperature-arrow-up' },
                { type: 'Hurricane Watch', icon: 'fa-hurricane' }
            ];

            const alertContainer = document.getElementById('alert-container');
            const loadingMsg = document.getElementById('loading-alerts');

            // --- 2. ALERT UI FUNCTIONS ---
            function createAlertCard(alert) {
                const timeStr = alert.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                return `
                    <div class="alert-card-enter bg-gray-800/60 rounded-xl p-4 border ${alert.severity.borderClass} hover:bg-gray-800 transition-colors cursor-pointer" onclick="focusOnMap(${alert.lat}, ${alert.lng}, '${alert.id}')">
                        <div class="flex justify-between items-start mb-2">
                            <div class="flex items-center gap-2">
                                <div class="w-8 h-8 rounded-lg ${alert.severity.bgClass} flex items-center justify-center">
                                    <i class="fa-solid ${alert.icon} ${alert.severity.textClass}"></i>
                                </div>
                                <div>
                                    <h3 class="font-bold text-sm text-white">${alert.type}</h3>
                                    <p class="text-xs text-gray-400"><i class="fa-solid fa-location-dot mr-1"></i>${alert.location}</p>
                                </div>
                            </div>
                            <span class="text-xs font-semibold px-2 py-1 rounded bg-gray-900 border border-gray-700 ${alert.severity.textClass}">
                                ${alert.severity.level}
                            </span>
                        </div>
                        <p class="text-xs text-gray-400 mt-2 line-clamp-2">${alert.details}</p>
                        <div class="mt-3 flex justify-between items-center text-[10px] text-gray-500">
                            <span>ID: ${alert.id}</span>
                            <span><i class="fa-regular fa-clock mr-1"></i>${timeStr}</span>
                        </div>
                    </div>
                `;
            }

            function addMarkerToMap(alert) {
                let iconHtml = '';
                if (alert.severity.level === 'Critical') {
                    iconHtml = `<div class="pulse-marker w-4 h-4 rounded-full"></div>`;
                } else {
                    iconHtml = `<div class="w-3 h-3 rounded-full border border-white" style="background-color: ${alert.severity.colorHex}; box-shadow: 0 0 8px ${alert.severity.colorHex};"></div>`;
                }

                const customIcon = L.divIcon({
                    className: 'custom-div-icon',
                    html: iconHtml,
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                });

                const marker = L.marker([alert.lat, alert.lng], { icon: customIcon }).addTo(map);
                
                const popupContent = `
                    <div class="text-brand-900 font-sans p-1">
                        <strong class="text-sm block mb-1" style="color: ${alert.severity.colorHex}">${alert.type}</strong>
                        <span class="text-xs text-gray-600 block">${alert.location}</span>
                        <hr class="my-1 border-gray-300">
                        <span class="text-xs font-semibold block">Severity: ${alert.severity.level}</span>
                    </div>
                `;
                marker.bindPopup(popupContent);
                markers[alert.id] = marker;
            }

            window.focusOnMap = function(lat, lng, id) {
                map.flyTo([lat, lng], 8, { animate: true, duration: 1.5 });
                if(markers[id]) {
                    setTimeout(() => { markers[id].openPopup(); }, 1500);
                }
            }

            function updateDashboard() {
                const criticalCount = alerts.filter(a => a.severity.level === 'Critical').length;
                document.getElementById('stat-critical').innerText = criticalCount;
                document.getElementById('stat-total').innerText = alerts.length;
                document.getElementById('alert-badge').innerText = alerts.length;
                document.getElementById('last-update').innerText = `Updated: ${new Date().toLocaleTimeString()}`;
            }

            function injectAlert(newAlert, focusMap = false) {
                if(loadingMsg) loadingMsg.remove(); 

                if (alerts.length >= 20) {
                    const oldest = alerts.pop(); 
                    if(markers[oldest.id]) {
                        map.removeLayer(markers[oldest.id]); 
                        delete markers[oldest.id];
                    }
                    if(alertContainer.lastElementChild) {
                        alertContainer.removeChild(alertContainer.lastElementChild);
                    }
                }
                
                alerts.unshift(newAlert); 
                
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = createAlertCard(newAlert);
                alertContainer.prepend(tempDiv.firstElementChild);

                addMarkerToMap(newAlert);
                updateDashboard();

                if(focusMap) {
                    window.focusOnMap(newAlert.lat, newAlert.lng, newAlert.id);
                }
            }

            // --- 3. HANDLE STANDALONE SEARCH ---
            document.getElementById('search-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const cityInput = document.getElementById('city-search').value.trim();
                if(!cityInput) return;

                const btn = document.getElementById('search-btn');
                const errorBox = document.getElementById('search-error');
                const errorTxt = document.getElementById('error-text');
                
                btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Searching...';
                btn.disabled = true;
                errorBox.classList.add('hidden');

                try {
                    const geocodeUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(cityInput)}&format=json&limit=1`;
                    const response = await fetch(geocodeUrl);
                    const data = await response.json();

                    if (!data || data.length === 0) {
                        throw new Error("Location not found. Try another city or country.");
                    }

                    const lat = parseFloat(data[0].lat);
                    const lng = parseFloat(data[0].lon);
                    let locName = data[0].display_name.split(',').slice(0, 2).join(',');

                    const event = eventTypes[Math.floor(Math.random() * eventTypes.length)];
                    const severity = severities[Math.floor(Math.random() * severities.length)];

                    const newAlert = {
                        id: `SRCH-${Math.floor(Math.random() * 100000)}`,
                        type: event.type,
                        icon: event.icon,
                        severity: severity,
                        location: locName,
                        lat: lat,
                        lng: lng,
                        timestamp: new Date(),
                        details: `[STANDALONE MODE] Simulated ${event.type.toLowerCase()} parameters triggered for ${locName}. Risk patterns indicate abnormal activity requiring monitoring.`
                    };

                    injectAlert(newAlert, true);
                    document.getElementById('city-search').value = ''; 

                } catch (err) {
                    errorTxt.innerText = err.message;
                    errorBox.classList.remove('hidden');
                } finally {
                    btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Search';
                    btn.disabled = false;
                }
            });

            // --- 4. MOCK BACKGROUND STREAM ---
            const mockLocations = [
                { name: "Miami, USA", lat: 25.7617, lng: -80.1918 },
                { name: "Mumbai, IND", lat: 19.0760, lng: 72.8777 },
                { name: "Manila, PHL", lat: 14.5995, lng: 120.9842 },
                { name: "Houston, USA", lat: 29.7604, lng: -95.3698 },
                { name: "Tokyo, JPN", lat: 35.6762, lng: 139.6503 }
            ];

            function processRandomBackgroundAlert() {
                const event = eventTypes[Math.floor(Math.random() * eventTypes.length)];
                const sevRand = Math.random();
                let severity = (sevRand > 0.85) ? severities[0] : (sevRand > 0.4) ? severities[1] : severities[2];
                const loc = mockLocations[Math.floor(Math.random() * mockLocations.length)];
                
                const newAlert = {
                    id: `ALRT-${Math.floor(Math.random() * 100000)}`,
                    type: event.type,
                    icon: event.icon,
                    severity: severity,
                    location: loc.name,
                    lat: loc.lat + ((Math.random() - 0.5) * 2), 
                    lng: loc.lng + ((Math.random() - 0.5) * 2),
                    timestamp: new Date(),
                    details: `Background anomaly detected. Sensor thresholds breached for ${event.type.toLowerCase()} conditions.`
                };
                injectAlert(newAlert, false);
            }

            setTimeout(() => {
                for(let i=0; i<3; i++) processRandomBackgroundAlert();
                const group = new L.featureGroup(Object.values(markers));
                map.fitBounds(group.getBounds().pad(0.5));
            }, 1000);

            setInterval(() => {
                if(Math.random() > 0.4) processRandomBackgroundAlert();
            }, 8000);

            window.addEventListener('resize', () => { map.invalidateSize(); });


            // --- 5. CHATBOT LOGIC FIX ---
            const chatToggle = document.getElementById('chatbot-toggle');
            const chatWindow = document.getElementById('chatbot-window');
            const chatClose = document.getElementById('chatbot-close');
            const chatInput = document.getElementById('chatbot-input');
            const chatSend = document.getElementById('chatbot-send');
            const chatMessages = document.getElementById('chatbot-messages');

            function toggleChat(e) {
                if(e) e.preventDefault();
                
                if (chatWindow.classList.contains('hidden')) {
                    // Show the window
                    chatWindow.classList.remove('hidden');
                    chatWindow.classList.add('flex');
                    
                    // Force the browser to reflow layout to ensure CSS transition triggers properly
                    void chatWindow.offsetWidth; 
                    
                    // Apply Tailwind visibility classes instead of custom CSS
                    chatWindow.classList.remove('opacity-0', 'translate-y-4');
                    chatWindow.classList.add('opacity-100', 'translate-y-0');
                    chatInput.focus(); // Automatically focus input for easy typing
                } else {
                    // Hide the window
                    chatWindow.classList.remove('opacity-100', 'translate-y-0');
                    chatWindow.classList.add('opacity-0', 'translate-y-4');
                    
                    // Wait for the opacity transition to finish before hiding it from layout entirely
                    setTimeout(() => {
                        chatWindow.classList.add('hidden');
                        chatWindow.classList.remove('flex');
                    }, 300);
                }
            }

            chatToggle.addEventListener('click', toggleChat);
            chatClose.addEventListener('click', toggleChat);

            function appendMessage(text, isUser) {
                const msgWrapper = document.createElement('div');
                msgWrapper.className = `flex ${isUser ? 'justify-end' : 'justify-start'} w-full`;
                
                const msgBubble = document.createElement('div');
                if (isUser) {
                    msgBubble.className = "bg-brand-accent text-brand-900 p-2.5 rounded-lg rounded-br-none max-w-[85%] text-xs shadow";
                } else {
                    msgBubble.className = "bg-gray-700 text-gray-100 p-2.5 rounded-lg rounded-bl-none max-w-[85%] text-xs shadow";
                }
                msgBubble.innerText = text;
                
                msgWrapper.appendChild(msgBubble);
                chatMessages.appendChild(msgWrapper);
                chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to bottom
            }

            function handleChatSubmit() {
                const text = chatInput.value.trim();
                if (!text) return;

                // 1. Show user message
                appendMessage(text, true);
                chatInput.value = '';

                // 2. Simulate bot typing & responding
                setTimeout(() => {
                    const query = text.toLowerCase();
                    let response = "I am a simulated assistant. In production, I will query your Python backend to answer that!";

                    // Basic Keyword Responses
                    if (query.includes('flood')) {
                        response = "Flood risks are calculated by measuring 1-hour rainfall, humidity, and wind speed. Search a city to see its specific simulated flood threat.";
                    } else if (query.includes('heat') || query.includes('hot')) {
                        response = "Heatwaves are detected when the combined temperature and humidity create a critical Heat Index. Ensure you check the 'Targeted Analysis' for your city.";
                    } else if (query.includes('hurricane') || query.includes('storm')) {
                        response = "We continuously monitor storm trajectories. A 'Critical' severity means immediate evacuation may be necessary.";
                    } else if (query.includes('hello') || query.includes('hi')) {
                        response = "Hello! Do you need help understanding the threat map, or do you have a question about extreme weather conditions?";
                    }

                    appendMessage(response, false);
                }, 600);
            }

            chatSend.addEventListener('click', handleChatSubmit);
            
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault(); // Prevents accidental page reload/form issues on Enter press
                    handleChatSubmit();
                }
            });
        });