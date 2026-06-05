// ==========================================
// FIX FOR ISSUE #86: Leaflet Theme Switcher
// ==========================================
const LIGHT_TILE_URL = 'https://{s}://{z}/{x}/{y}{r}.png';
const DARK_TILE_URL = 'https://{s}://{z}/{x}/{y}{r}.png';
const MAP_ATTRIBUTION = '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>';

let globalActiveMapLayer = null;
let mapDarkModeState = false;

// Intercept Leaflet to manage themes automatically
if (window.L && window.L.tileLayer) {
    const originalTileLayer = window.L.tileLayer;
    window.L.tileLayer = function (url, options) {
        const targetUrl = mapDarkModeState ? DARK_TILE_URL : LIGHT_TILE_URL;
        const layer = originalTileLayer(targetUrl, { ...options, attribution: MAP_ATTRIBUTION });
        globalActiveMapLayer = layer;
        return layer;
    };
    Object.assign(window.L.tileLayer, originalTileLayer);
}

function toggleMapTheme() {
    if (!globalActiveMapLayer || !window.L) return;

    const mapContainers = document.querySelectorAll('.leaflet-container');
    mapContainers.forEach(container => {
        const activeMapInstance = container._leaflet_map || null;
        if (activeMapInstance) {
            globalActiveMapLayer.remove();
            mapDarkModeState = !mapDarkModeState;
            const newUrl = mapDarkModeState ? DARK_TILE_URL : LIGHT_TILE_URL;
            globalActiveMapLayer = window.L.tileLayer(newUrl).addTo(activeMapInstance);
        }
    });

    if (mapContainers.length === 0) {
        mapDarkModeState = !mapDarkModeState;
    }
}

// CRITICAL FIX FOR ISSUE #84: Global Chart Tracker
// ==========================================
let climateChartInstance = null;

// Hook into Chart.js to intercept creation and destroy older leaking instances automatically
if (window.Chart) {
    const OriginalChart = window.Chart;
    window.Chart = function (ctx, config) {
        if (climateChartInstance !== null && typeof climateChartInstance.destroy === 'function') {
            try {
                climateChartInstance.destroy();
            } catch (e) {
                console.warn("Instance cleanup handled:", e);
            }
        }
        climateChartInstance = new OriginalChart(ctx, config);
        return climateChartInstance;
    };
    // Copy static properties over to the patched constructor
    Object.assign(window.Chart, OriginalChart);
}

// ==========================================
// Your Original Weather API Logic

// ==========================================
function resolveApiUrl(){
    // Prefer explicit backend URL injected by the HTML page.
    // Set window.__BACKEND_URL__ to your Flask/Gunicorn service base URL in production.
    if (window.__BACKEND_URL__ && typeof window.__BACKEND_URL__ === 'string' && window.__BACKEND_URL__.trim() !== '') {
        return window.__BACKEND_URL__.replace(/\/+$/, '') + '/weather';
    }

    // Local dev fallback.
    if (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost") {
        return "http://127.0.0.1:5000/weather";
    }


    // Production fallback: assume backend is reachable at same origin.
    // This is correct only when frontend and backend are served by the same host.
    return window.location.origin + "/weather";
}


const API_URL = resolveApiUrl();


async function getWeatherData() {
    const city = document.getElementById("city").value;
    const state = document.getElementById("state").value;
    const country = document.getElementById("country").value;
    const loading = document.getElementById("loading");
    const weatherCard = document.getElementById("weather-card");
    const alertBox = document.getElementById("alert-box");

    if (city.trim() === "" || state.trim() === "" || country.trim() === "") {
        alert("Please fill all fields.");
        return;
    }

    loading.classList.remove("hidden");
    weatherCard.classList.add("hidden");

    try {
        const response = await fetch(
            API_URL,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    city: city,
                    state: state,
                    country: country
                })
            }
        );

        if (!response.ok) {
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        loading.classList.add("hidden");

        if (!data.success) {
            alert(data.message);
            return;
        }

        document.getElementById("location").innerText =
            `${data.location.city}, ${data.location.state}, ${data.location.country}`;

        document.getElementById("temperature").innerText = `${data.weather.temperature} °C`;
        document.getElementById("humidity").innerText = `${data.weather.humidity} %`;
        document.getElementById("rainfall").innerText = `${data.weather.rainfall} mm`;
        document.getElementById("wind").innerText = `${data.weather.wind_speed} km/h`;
        document.getElementById("flood-risk").innerText = data.risks.flood_risk;
        document.getElementById("heat-risk").innerText = data.risks.heat_risk;

        let alertsHTML = "";
        data.alerts.forEach(alertMessage => {
            alertsHTML += `
                <div class="notification">
                    ${alertMessage}
                </div>
            `;
        });

        alertBox.innerHTML = alertsHTML;
        alertBox.classList.remove("hidden");
        weatherCard.classList.remove("hidden");

    } catch (error) {
        console.error(error);
        loading.classList.add("hidden");
        alert("Backend server is not running.");
    }
}

// Hook map toggle up to the UI theme buttons
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('map-theme-toggle') || document.getElementById('theme-toggle');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleMapTheme);
    }
});

// ==========================================
// Lifecycle Clean-up Hook for Route Changes
// ==========================================
window.addEventListener('beforeunload', () => {
    if (climateChartInstance !== null && typeof climateChartInstance.destroy === 'function') {
        climateChartInstance.destroy();
    }
});
function generateClimateInsight(localTrend, globalTrend, location) {
    const diff = localTrend - globalTrend;
    const percent = ((diff / globalTrend) * 100).toFixed(1);

    if (diff > 0) {
        return `🌍 ${location} is warming ${percent}% faster than global average.`;
    }
    else if (diff < 0) {
        return `❄️ ${location} is warming slower than global average.`;
    }
    else {
        return `🌿 ${location} matches global climate trends.`;
    }
}
function detectAnomalies(data, threshold = 2) {
    const mean = data.reduce((a, b) => a + b, 0) / data.length;

    const variance = data.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / data.length;

    const stdDev = Math.sqrt(variance);

    return data.map(value => {
        const zScore = (value - mean) / stdDev;

        return {
            value,
            isAnomaly: Math.abs(zScore) > threshold,
            zScore
        };
    });
}
window.onload = function () {

    const climateInsightElement =
        document.getElementById("climate-insight");

    const anomalyResultElement =
        document.getElementById("anomaly-result");

    if (climateInsightElement) {
        const insight = generateClimateInsight(
            1.8,
            1.2,
            "Andhra Pradesh"
        );

        climateInsightElement.innerText = insight;
    }

    if (anomalyResultElement) {
        const tempData = [28, 29, 30, 45, 31, 29];

        const results = detectAnomalies(tempData);

        const anomalies = results.filter(
            r => r.isAnomaly
        );

        anomalyResultElement.innerHTML =
            anomalies.length === 0
                ? "✅ No unusual climate spikes detected"
                : anomalies
                    .map(
                        a =>
                            `⚠️ Anomaly: ${a.value}°C (z=${a.zScore.toFixed(2)})`
                    )
                    .join("<br>");
    }
};
const themeToggle = document.getElementById("theme-toggle");

// Load saved theme
const savedTheme = localStorage.getItem("theme");

if (savedTheme === "light") {
    document.body.classList.add("light-mode");
    if (themeToggle) {
        themeToggle.textContent = "☀️";
    }
}

// Toggle theme
if (savedTheme === "light") {
    document.body.classList.add("light-mode");
    if (themeToggle) {
        themeToggle.textContent = "☀";
    }
}

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        document.body.classList.toggle("light-mode");

        if (document.body.classList.contains("light-mode")) {
            localStorage.setItem("theme", "light");
            themeToggle.textContent = "☀";
        } else {
            localStorage.setItem("theme", "dark");
            themeToggle.textContent = "☾";
        }
    });
}
const scrollTopBtn = document.getElementById("scrollTopBtn");

if (scrollTopBtn) {
    window.addEventListener("scroll", () => {
        if (window.scrollY > 300) {
            scrollTopBtn.classList.add("show");
        } else {
            scrollTopBtn.classList.remove("show");
        }
    });

    scrollTopBtn.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });
}