let tempChartInstance = null;
let humidityChartInstance = null;
let rainfallChartInstance = null;

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

    hideMessage();

    results.classList.add('hidden');

    results.classList.remove('is-visible');

    alertBox.classList.add('hidden');

    alertBox.innerHTML = '';

    destroyExistingCharts();

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

        if (!data.success) {

            destroyExistingCharts();

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

        renderWeatherTrends(data.forecast);

        results.classList.remove('hidden');

        requestAnimationFrame(() => {

            results.classList.add('is-visible');
        });

    } catch (error) {

        console.error(error);

        loading.classList.add('hidden');

        destroyExistingCharts();

        showMessage(
            'Backend server is not running.',
            'is-error'
        );
    }
}

function destroyExistingCharts() {
    if (tempChartInstance) {
        tempChartInstance.destroy();
        tempChartInstance = null;
    }
    if (humidityChartInstance) {
        humidityChartInstance.destroy();
        humidityChartInstance = null;
    }
    if (rainfallChartInstance) {
        rainfallChartInstance.destroy();
        rainfallChartInstance = null;
    }
}

function renderWeatherTrends(forecastData) {
    destroyExistingCharts();

    const container = document.getElementById('trends-container');
    if (!container) return;

    // Recreate canvas structures to avoid memory leaks/ghosting
    container.innerHTML = `
        <div class="trend-chart-box">
            <h4>Temperature Trend</h4>
            <div class="chart-wrapper">
                <canvas id="tempChart" aria-label="Temperature Trend Chart" role="img"></canvas>
            </div>
        </div>

        <div class="trend-chart-box">
            <h4>Humidity Trend</h4>
            <div class="chart-wrapper">
                <canvas id="humidityChart" aria-label="Humidity Trend Chart" role="img"></canvas>
            </div>
        </div>

        <div class="trend-chart-box">
            <h4>Rainfall Trend</h4>
            <div class="chart-wrapper">
                <canvas id="rainfallChart" aria-label="Rainfall Trend Chart" role="img"></canvas>
            </div>
        </div>
    `;

    if (!forecastData || !Array.isArray(forecastData) || forecastData.length === 0) {
        container.innerHTML = `
            <div class="trends-empty-state">
                <span>⚠️</span>
                <p>Real-time 5-day forecast trends unavailable for this location.</p>
            </div>
        `;
        return;
    }

    const labels = [];
    const tempValues = [];
    const humidityValues = [];
    const rainfallValues = [];

    // Map 5-day / 3-hour forecast to 12-hour intervals (every 4th item) to display 10 real data points
    for (let i = 0; i < forecastData.length; i += 4) {
        const item = forecastData[i];
        if (!item || item.time === undefined) continue;

        const date = new Date(item.time * 1000);
        const day = date.toLocaleDateString('en-US', { weekday: 'short' });
        const hours = date.getHours();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        const hourLabel = `${hours % 12 || 12} ${ampm}`;

        labels.push(`${day} ${hourLabel}`);
        tempValues.push(item.temp !== undefined ? Number(item.temp.toFixed(1)) : 0);
        humidityValues.push(item.humidity !== undefined ? Math.round(item.humidity) : 0);
        rainfallValues.push(item.rainfall !== undefined ? Number(item.rainfall.toFixed(1)) : 0);
    }

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                titleFont: { family: 'Poppins', size: 12, weight: '600' },
                bodyFont: { family: 'Poppins', size: 12 },
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                padding: 10,
                displayColors: false
            }
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.04)',
                    borderColor: 'rgba(255, 255, 255, 0.08)'
                },
                ticks: {
                    color: '#94a3b8',
                    font: { family: 'Poppins', size: 10 }
                }
            },
            y: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.04)',
                    borderColor: 'rgba(255, 255, 255, 0.08)'
                },
                ticks: {
                    color: '#94a3b8',
                    font: { family: 'Poppins', size: 10 }
                }
            }
        }
    };

    try {
        // 1. Temperature Chart (Line)
        const tempCtx = document.getElementById('tempChart').getContext('2d');
        const tempGradient = tempCtx.createLinearGradient(0, 0, 0, 200);
        tempGradient.addColorStop(0, 'rgba(245, 158, 11, 0.22)');
        tempGradient.addColorStop(1, 'rgba(245, 158, 11, 0.0)');

        tempChartInstance = new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    data: tempValues,
                    borderColor: '#f59e0b',
                    borderWidth: 2,
                    pointBackgroundColor: '#f59e0b',
                    pointBorderColor: 'rgba(255, 255, 255, 0.4)',
                    pointHoverRadius: 6,
                    pointRadius: 3,
                    tension: 0.4,
                    fill: true,
                    backgroundColor: tempGradient
                }]
            },
            options: {
                ...chartOptions,
                scales: {
                    ...chartOptions.scales,
                    y: {
                        ...chartOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Temperature (°C)',
                            color: '#94a3b8',
                            font: { family: 'Poppins', size: 11, weight: '600' }
                        }
                    }
                }
            }
        });

        // 2. Humidity Chart (Line)
        const humCtx = document.getElementById('humidityChart').getContext('2d');
        const humGradient = humCtx.createLinearGradient(0, 0, 0, 200);
        humGradient.addColorStop(0, 'rgba(56, 189, 248, 0.22)');
        humGradient.addColorStop(1, 'rgba(56, 189, 248, 0.0)');

        humidityChartInstance = new Chart(humCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    data: humidityValues,
                    borderColor: '#38bdf8',
                    borderWidth: 2,
                    pointBackgroundColor: '#38bdf8',
                    pointBorderColor: 'rgba(255, 255, 255, 0.4)',
                    pointHoverRadius: 6,
                    pointRadius: 3,
                    tension: 0.4,
                    fill: true,
                    backgroundColor: humGradient
                }]
            },
            options: {
                ...chartOptions,
                scales: {
                    ...chartOptions.scales,
                    y: {
                        ...chartOptions.scales.y,
                        suggestedMin: 0,
                        suggestedMax: 100,
                        title: {
                            display: true,
                            text: 'Humidity (%)',
                            color: '#94a3b8',
                            font: { family: 'Poppins', size: 11, weight: '600' }
                        }
                    }
                }
            }
        });

        // 3. Rainfall Chart (Bar)
        const rainCtx = document.getElementById('rainfallChart').getContext('2d');
        const rainGradient = rainCtx.createLinearGradient(0, 0, 0, 200);
        rainGradient.addColorStop(0, 'rgba(14, 165, 233, 0.7)');
        rainGradient.addColorStop(1, 'rgba(14, 165, 233, 0.1)');

        rainfallChartInstance = new Chart(rainCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: rainfallValues,
                    backgroundColor: rainGradient,
                    borderColor: '#0ea5e9',
                    borderWidth: 1.5,
                    borderRadius: 5,
                    borderSkipped: false
                }]
            },
            options: {
                ...chartOptions,
                scales: {
                    ...chartOptions.scales,
                    y: {
                        ...chartOptions.scales.y,
                        suggestedMin: 0,
                        title: {
                            display: true,
                            text: 'Rainfall (mm)',
                            color: '#94a3b8',
                            font: { family: 'Poppins', size: 11, weight: '600' }
                        }
                    }
                }
            }
        });
    } catch (e) {
        console.error("Error rendering charts:", e);
    }
}