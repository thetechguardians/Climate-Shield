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
    const analyzeBtn = document.getElementById('analyze-btn');

    const showMessage = (message, tone) => {

        messageBox.textContent = message;

        messageBox.classList.remove(
            'hidden',
            'is-error',
            'is-success'
        );

        if (tone) {

            messageBox.classList.add(tone);
        }
    };

    const hideMessage = () => {

        messageBox.textContent = '';

        messageBox.classList.add('hidden');

        messageBox.classList.remove(
            'is-error',
            'is-success'
        );
    };

    if (!city || !state || !country) {

        showMessage(
            'Please fill all fields.',
            'is-error'
        );

        return;
    }

    loading.classList.remove('hidden');
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';


    hideMessage();

    results.classList.add('hidden');

    results.classList.remove('is-visible');

    alertBox.classList.add('hidden');

    alertBox.innerHTML = '';

    try {

        const response = await fetch(API_URL, {

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
        analyzeBtn.disabled = false;
        analyzeBtn.innerText = 'Analyze Climate Risk';

        if (!data.success) {

            showMessage(
                data.message || 'Location not found.',
                'is-error'
            );

            return;
        }

        hideMessage();

        document.getElementById('location').innerText =

            `${data.location.city},
             ${data.location.state},
             ${data.location.country}`;

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

            alertsHTML += `

                <div class="notification">

                    ${alertMessage}

                </div>

            `;
        });

        alertBox.innerHTML = alertsHTML;

        alertBox.classList.remove('hidden');

        resultStatus.innerText =
            "Climate analysis completed";

        resultSummary.innerText =
            "Live weather and risk analysis generated successfully.";

        statusPill.innerText =
            "Analysis Complete";

        results.classList.remove('hidden');

        requestAnimationFrame(() => {

            results.classList.add('is-visible');
        });

    } catch (error) {

        console.error(error);

        loading.classList.add('hidden');
        analyzeBtn.disabled = false;
       analyzeBtn.textContent = 'Analyze Climate Risk';

        showMessage(
            'Backend server is not running.',
            'is-error'
        );
    }
}
function clearResults() {

    document.getElementById('city').value = '';

    document.getElementById('state').value = '';

    document.getElementById('country').value = '';

    document.getElementById('results').classList.add('hidden');

    document.getElementById('alert-box').classList.add('hidden');

    document.getElementById('message-box').classList.add('hidden');
}