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
        if (tone) {
            messageBox.classList.add(tone);
        }
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
    alertBox.classList.remove('alert-danger', 'alert-warning');
    alertBox.innerHTML = '';
    resultStatus.innerText = 'Preparing live climate snapshot';
    resultSummary.innerText = 'Fetching the latest weather data and computing a location-specific risk summary.';
    statusPill.innerText = 'Analyzing';

    try {
        const response = await fetch(window.location.origin + '/weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                city,
                state,
                country
            })
        });

        const data = await response.json();
        loading.classList.add('hidden');

        if (!data.success) {
            showMessage(data.message || 'Location not found.', 'is-error');
            resultStatus.innerText = 'Location not found';
            resultSummary.innerText = 'Try another city, state, or country and run the analysis again.';
            statusPill.innerText = 'No match';
            results.classList.remove('hidden');
            requestAnimationFrame(() => {
                results.classList.add('is-visible');
            });
            return;
        }

        hideMessage();

        const floodRiskText = data.risks.flood_risk;
        const heatRiskText = data.risks.heat_risk;
        const hasHighRiskAlert = data.alerts.some(alertMessage =>
            alertMessage.includes('Flood Risk Detected') ||
            alertMessage.includes('Heatwave Risk Detected')
        );
        const climateSeverity = hasHighRiskAlert ? 'High vigilance recommended' : 'Conditions appear stable';
        const climateSummary = hasHighRiskAlert
            ? 'The current signals suggest elevated weather risk. Review the detailed alerts before planning outdoor activity.'
            : 'No major alerts were detected. The location appears relatively stable based on the current weather snapshot.';

        document.getElementById('location').innerText =
            `${data.location.city}, ${data.location.state}, ${data.location.country}`;
        document.getElementById('temperature').innerText = `${data.weather.temperature} °C`;
        document.getElementById('humidity').innerText = `${data.weather.humidity} %`;
        document.getElementById('rainfall').innerText = `${data.weather.rainfall} mm`;
        document.getElementById('wind').innerText = `${data.weather.wind_speed} km/h`;
        document.getElementById('flood-risk').innerText = floodRiskText;
        document.getElementById('heat-risk').innerText = heatRiskText;

        resultStatus.innerText = climateSeverity;
        resultSummary.innerText = climateSummary;
        statusPill.innerText = hasHighRiskAlert ? 'Elevated risk' : 'Low risk';
        statusPill.style.borderColor = hasHighRiskAlert ? 'rgba(239, 68, 68, 0.38)' : 'rgba(34, 197, 94, 0.32)';
        statusPill.style.background = hasHighRiskAlert ? 'rgba(239, 68, 68, 0.12)' : 'rgba(34, 197, 94, 0.12)';
        statusPill.style.color = hasHighRiskAlert ? '#fecaca' : '#bbf7d0';

        const alertsHTML = data.alerts.length > 0
            ? data.alerts
                .map(alertMessage => `<div class="notification">${alertMessage}</div>`)
                .join('')
            : '<div class="notification">No major alerts detected for this location.</div>';

        alertBox.innerHTML = alertsHTML;
        alertBox.classList.remove('hidden');

        alertBox.classList.add(hasHighRiskAlert ? 'alert-danger' : 'alert-warning');
        alertBox.classList.remove(hasHighRiskAlert ? 'alert-warning' : 'alert-danger');
        results.classList.remove('hidden');
        requestAnimationFrame(() => {
            results.classList.add('is-visible');
        });
    } catch (error) {
        console.log(error);
        loading.classList.add('hidden');
        showMessage('Backend server is not running.', 'is-error');
    }
}
