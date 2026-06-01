const API_URL =
    window.location.hostname === "127.0.0.1"
    ||
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:5000/weather"
        : window.location.origin + "/weather";

async function getWeatherData() {

    const city = document.getElementById('city').value.trim();
    const state = document.getElementById('state').value.trim();
    const country = document.getElementById('country').value.trim();
    const loading = document.getElementById('loading');
    const messageBox = document.getElementById('message-box');
    const results = document.getElementById('results');
    const alertBox = document.getElementById('alert-box');
    const resultStatus = document.getElementById('result-status');
    const resultSummary = document.getElementById('result-summary');
    const statusPill = document.getElementById('status-pill');

    const showMessage = (message, tone) => {
        messageBox.textContent = message;
        messageBox.classList.remove('hidden', 'is-error', 'is-success');
        if (tone) messageBox.classList.add(tone);
    };

    const hideMessage = () => {
        messageBox.textContent = '';
        messageBox.classList.add('hidden');
        messageBox.classList.remove('is-error', 'is-success');
    };

    if (!city || !state || !country) {
        showMessage('Please fill all fields.', 'is-error');
        return;
    }

    loading.classList.remove('hidden');
    hideMessage();
    results.classList.add('hidden');
    results.classList.remove('is-visible');
    alertBox.classList.add('hidden');
    alertBox.innerHTML = '';

    try {

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city, state, country })
        });

        const data = await response.json();

        loading.classList.add('hidden');

        if (!data.success) {
            showMessage(data.message || 'Location not found.', 'is-error');
            return;
        }

        hideMessage();

        document.getElementById('location').innerText =
            `${data.location.city}, ${data.location.state}, ${data.location.country}`;

        document.getElementById('temperature').innerText =
            `${data.weather.temperature} °C`;

        document.getElementById('humidity').innerText =
            `${data.weather.humidity} %`;

        document.getElementById('rainfall').innerText =
            `${data.weather.rainfall} mm`;

        document.getElementById('wind').innerText =
            `${data.weather.wind_speed} km/h`;

        document.getElementById('flood-risk').innerText =
            data.risks.flood_risk;

        document.getElementById('heat-risk').innerText =
            data.risks.heat_risk;

        let alertsHTML = "";
        data.alerts.forEach(alertMessage => {
            alertsHTML += `<div class="notification">${alertMessage}</div>`;
        });

        alertBox.innerHTML = alertsHTML;
        alertBox.classList.remove('hidden');

        resultStatus.innerText = "Climate analysis completed";
        resultSummary.innerText = "Live weather and risk analysis generated successfully.";
        statusPill.innerText = "Analysis Complete";

        const measures = getPreventiveMeasures(data.risks.flood_risk, data.risks.heat_risk);
        const measuresBox = document.getElementById('preventive-measures');
        document.getElementById('measures-content').innerHTML = measures;
        measuresBox.classList.remove('hidden');

        results.classList.remove('hidden');
        requestAnimationFrame(() => {
            results.classList.add('is-visible');
        });

    } catch (error) {
        console.error(error);
        loading.classList.add('hidden');
        showMessage('Backend server is not running.', 'is-error');
    }
}

function getPreventiveMeasures(floodRisk, heatRisk) {

    floodRisk = String(floodRisk);
    heatRisk = String(heatRisk);

    let cards = '';

    if (parseFloat(floodRisk) >= 0.5){
        cards += `
            <div class="measure-card flood-measure">
                <h4>🌊 Flood Safety</h4>
                <div class="measure-phase">
                    <strong>Before</strong>
                    <ul>
                        <li>Move valuables to higher floors</li>
                        <li>Keep emergency kit ready (water, food, documents)</li>
                        <li>Know your nearest evacuation route</li>
                    </ul>
                </div>
                <div class="measure-phase">
                    <strong>During</strong>
                    <ul>
                        <li>Avoid walking or driving through floodwater</li>
                        <li>Stay off bridges over fast-moving water</li>
                        <li>Move to higher ground immediately</li>
                    </ul>
                </div>
                <div class="measure-phase">
                    <strong>After</strong>
                    <ul>
                        <li>Do not enter buildings until declared safe</li>
                        <li>Avoid contact with floodwater (may be contaminated)</li>
                        <li>Document damage for insurance</li>
                    </ul>
                </div>
            </div>
        `;
    }

    if (parseFloat(heatRisk) >= 0.5) {
        cards += `
            <div class="measure-card heat-measure">
                <h4>🌡 Heatwave Safety</h4>
                <div class="measure-phase">
                    <strong>Before</strong>
                    <ul>
                        <li>Stock up on water and electrolyte drinks</li>
                        <li>Identify nearby cooling centers</li>
                        <li>Check on elderly neighbors and family</li>
                    </ul>
                </div>
                <div class="measure-phase">
                    <strong>During</strong>
                    <ul>
                        <li>Stay indoors during peak hours (12pm–4pm)</li>
                        <li>Drink water every 15–20 minutes</li>
                        <li>Wear light, loose, light-colored clothing</li>
                    </ul>
                </div>
                <div class="measure-phase">
                    <strong>After</strong>
                    <ul>
                        <li>Watch for signs of heat exhaustion</li>
                        <li>Gradually resume outdoor activities</li>
                        <li>Rehydrate and rest properly</li>
                    </ul>
                </div>
            </div>
        `;
    }

    if (cards === '') {
        cards = `<p class="no-measures">✅ No major risks detected. Stay alert and monitor weather updates regularly.</p>`;
    }

    return cards;
}