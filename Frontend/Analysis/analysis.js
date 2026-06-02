const API_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000/weather"
    : window.location.origin + "/weather";

// Global map and chart variables to prevent recreation bugs
let mapInstance = null;
let weatherChartInstance = null;
let riskChartInstance = null;

// Expose active location data globally for the chatbot to access
window.activeClimateReport = null;

async function getWeatherData() {
  const city = document.getElementById("city").value.trim();
  const state = document.getElementById("state").value.trim();
  const country = document.getElementById("country").value.trim();
  const loading = document.getElementById("loading");
  const messageBox = document.getElementById("message-box");
  const results = document.getElementById("results");
  const alertBox = document.getElementById("alert-box");
  const resultStatus = document.getElementById("result-status");
  const resultSummary = document.getElementById("result-summary");
  const statusPill = document.getElementById("status-pill");
  const analyzeBtn = document.getElementById("analyze-btn");
  const demoIndicator = document.getElementById("demo-mode-indicator");
  const dispatchLogsBox = document.getElementById("dispatch-logs-box");

  const showMessage = (message, tone) => {
    messageBox.textContent = message;
    messageBox.classList.remove("hidden", "is-error", "is-success");
    if (tone) {
      messageBox.classList.add(tone);
    }
  };

  const hideMessage = () => {
    messageBox.textContent = "";
    messageBox.classList.add("hidden");
    messageBox.classList.remove("is-error", "is-success");
  };

  if (!city || !state || !country) {
    showMessage("Please fill all fields.", "is-error");
    return;
  }

  loading.classList.remove("hidden");
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";

  hideMessage();
  results.classList.add("hidden");
  results.classList.remove("is-visible");
  alertBox.classList.add("hidden");
  alertBox.innerHTML = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ city, state, country }),
    });

    const data = await response.json();
    loading.classList.add("hidden");
    analyzeBtn.disabled = false;
    analyzeBtn.innerText = "Analyze Climate Risk";

    if (!data.success) {
      showMessage(data.message || "Location not found.", "is-error");
      return;
    }

    hideMessage();

    // Update active report in window context
    window.activeClimateReport = data;

    // UI Text updates
    document.getElementById("location").innerText =
      `${data.location.city}, ${data.location.state}, ${data.location.country}`;
    document.getElementById("temperature").innerText =
      `${data.weather.temperature} °C`;
    document.getElementById("humidity").innerText =
      `${data.weather.humidity} %`;
    document.getElementById("rainfall").innerText =
      `${data.weather.rainfall} mm`;
    document.getElementById("wind").innerText =
      `${data.weather.wind_speed} km/h`;

    // Risks scores
    document.getElementById("flood-risk").innerText = data.risks.flood_risk;
    document.getElementById("heat-risk").innerText = data.risks.heat_risk;
    document.getElementById("wildfire-risk").innerText =
      data.risks.wildfire_risk;
    document.getElementById("cyclone-risk").innerText = data.risks.cyclone_risk;
    document.getElementById("drought-risk").innerText = data.risks.drought_risk;

    // Demo indicator
    if (data.demo_mode) {
      demoIndicator.classList.remove("hidden");
    } else {
      demoIndicator.classList.add("hidden");
    }

    // Render Alerts
    let alertsHTML = "";
    data.alerts.forEach((alertMessage) => {
      let badgeClass = alertMessage.includes("✅")
        ? "alert-warning"
        : "alert-danger";
      alertsHTML += `<div class="alert-box ${badgeClass}">${alertMessage}</div>`;
    });
    alertBox.innerHTML = alertsHTML;
    alertBox.classList.remove("hidden");

    // Render Leaflet Map
    const lat = data.location.latitude;
    const lon = data.location.longitude;

    if (!mapInstance) {
      mapInstance = L.map("map").setView([lat, lon], 10);
      L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
          subdomains: "abcd",
          maxZoom: 20,
        },
      ).addTo(mapInstance);
    } else {
      mapInstance.setView([lat, lon], 10);
      // Clear old layers (except the base tile layer)
      mapInstance.eachLayer((layer) => {
        if (layer instanceof L.Marker || layer instanceof L.Circle) {
          mapInstance.removeLayer(layer);
        }
      });
    }

    // Draw a circle centered around the risk scale
    const maxRisk = Math.max(
      data.risks.flood_risk,
      data.risks.heat_risk,
      data.risks.wildfire_risk,
      data.risks.cyclone_risk,
      data.risks.drought_risk,
    );
    let circleColor = "#22c55e"; // green (safe)
    if (maxRisk >= 0.7) {
      circleColor = "#ef4444"; // red (danger)
    } else if (maxRisk >= 0.5) {
      circleColor = "#f59e0b"; // orange (warning)
    }

    L.circle([lat, lon], {
      color: circleColor,
      fillColor: circleColor,
      fillOpacity: 0.15,
      radius: 10000, // 10km radius
    }).addTo(mapInstance);

    const mapMarker = L.marker([lat, lon]).addTo(mapInstance);
    mapMarker
      .bindPopup(
        `
            <div style="min-width: 160px; font-family: sans-serif;">
                <h4 style="margin: 0 0 5px 0; color: #fff;">${data.location.city}</h4>
                <p style="margin: 0; font-size: 0.8rem; line-height: 1.4; color: #cbd5e1;">
                    🌡️ Temp: ${data.weather.temperature} °C<br>
                    🌊 Flood Risk: ${data.risks.flood_risk}<br>
                    🔥 Heat Risk: ${data.risks.heat_risk}<br>
                    🌲 Wildfire: ${data.risks.wildfire_risk}<br>
                    🌀 Cyclone: ${data.risks.cyclone_risk}
                </p>
            </div>
        `,
      )
      .openPopup();

    // Render 5-Day Forecast
    const forecastContainer = document.getElementById(
      "forecast-cards-container",
    );
    forecastContainer.innerHTML = "";

    data.forecast.forEach((day) => {
      const dateObj = new Date(day.date);
      const formattedDate = dateObj.toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      });

      const maxDayRisk = Math.max(
        day.risks.flood_risk,
        day.risks.heat_risk,
        day.risks.wildfire_risk,
        day.risks.cyclone_risk,
        day.risks.drought_risk,
      );
      const isDanger = maxDayRisk >= 0.65;
      const alertTag = isDanger ? "⚠️ High Hazard" : "✅ Normal";

      const card = document.createElement("div");
      card.className = "forecast-card";
      card.innerHTML = `
                <div class="forecast-date">${formattedDate}</div>
                <div class="forecast-temp">${day.temperature} °C</div>
                <div class="forecast-details">
                    <span>💧 Humid: ${day.humidity}%</span>
                    <span>🌧 Rain: ${day.rainfall} mm</span>
                    <span>🌪 Wind: ${day.wind_speed} km/h</span>
                </div>
                <div class="forecast-risk-indicator ${isDanger ? "has-danger" : ""}">${alertTag}</div>
            `;
      forecastContainer.appendChild(card);
    });

    // Initialize / Update Charts
    const forecastLabels = data.forecast.map((day) => {
      const dateObj = new Date(day.date);
      return dateObj.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      });
    });

    // Weather Chart (Temp Line, Rain Bar)
    if (weatherChartInstance) {
      weatherChartInstance.destroy();
    }
    const ctx1 = document.getElementById("weatherChart").getContext("2d");
    weatherChartInstance = new Chart(ctx1, {
      type: "bar",
      data: {
        labels: forecastLabels,
        datasets: [
          {
            label: "Rainfall (mm)",
            data: data.forecast.map((day) => day.rainfall),
            backgroundColor: "rgba(56, 189, 248, 0.4)",
            borderColor: "#38bdf8",
            borderWidth: 1,
            yAxisID: "yRain",
          },
          {
            label: "Temperature (°C)",
            data: data.forecast.map((day) => day.temperature),
            type: "line",
            borderColor: "#ef4444",
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            tension: 0.35,
            fill: true,
            yAxisID: "yTemp",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#cbd5e1" } },
        },
        scales: {
          x: {
            grid: { color: "rgba(255,255,255,0.05)" },
            ticks: { color: "#94a3b8" },
          },
          yTemp: {
            type: "linear",
            position: "left",
            ticks: { color: "#ef4444" },
            grid: { color: "rgba(255,255,255,0.05)" },
          },
          yRain: {
            type: "linear",
            position: "right",
            ticks: { color: "#38bdf8" },
            grid: { drawOnChartArea: false },
          },
        },
      },
    });

    // Multi-Risk Index Trends Chart
    if (riskChartInstance) {
      riskChartInstance.destroy();
    }
    const ctx2 = document.getElementById("riskChart").getContext("2d");
    riskChartInstance = new Chart(ctx2, {
      type: "line",
      data: {
        labels: forecastLabels,
        datasets: [
          {
            label: "Flood",
            data: data.forecast.map((day) => day.risks.flood_risk),
            borderColor: "#ef4444",
            tension: 0.3,
            fill: false,
          },
          {
            label: "Heat",
            data: data.forecast.map((day) => day.risks.heat_risk),
            borderColor: "#f59e0b",
            tension: 0.3,
            fill: false,
          },
          {
            label: "Wildfire",
            data: data.forecast.map((day) => day.risks.wildfire_risk),
            borderColor: "#f97316",
            tension: 0.3,
            fill: false,
          },
          {
            label: "Cyclone",
            data: data.forecast.map((day) => day.risks.cyclone_risk),
            borderColor: "#a855f7",
            tension: 0.3,
            fill: false,
          },
          {
            label: "Drought",
            data: data.forecast.map((day) => day.risks.drought_risk),
            borderColor: "#eab308",
            tension: 0.3,
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#cbd5e1" } },
        },
        scales: {
          x: {
            grid: { color: "rgba(255,255,255,0.05)" },
            ticks: { color: "#94a3b8" },
          },
          y: {
            min: 0,
            max: 1.0,
            ticks: { color: "#94a3b8" },
            grid: { color: "rgba(255,255,255,0.05)" },
          },
        },
      },
    });

    // Generate Dispatch Logs
    dispatchLogsBox.innerHTML = "";
    const addLog = (msg, tone) => {
      const timeStr = new Date().toLocaleTimeString();
      const entry = document.createElement("div");
      entry.className = `log-entry ${tone}`;
      entry.innerHTML = `[${timeStr}] <strong>${tone.toUpperCase()}:</strong> ${msg}`;
      dispatchLogsBox.appendChild(entry);
    };

    addLog(
      `Monitoring node activated at Lat ${lat.toFixed(4)}, Lon ${lon.toFixed(4)}`,
      "success",
    );
    if (data.demo_mode) {
      addLog(
        `OpenWeather key unconfigured/expired. Defaulting to Demo Mode simulation.`,
        "warning",
      );
    }

    data.alerts.forEach((alert) => {
      if (alert.includes("✅")) {
        addLog(
          `No active hazards flagged. Parameters sit within safety standard threshold limit.`,
          "success",
        );
      } else {
        addLog(
          `CRITICAL BROADCAST: ${alert} active in the target area!`,
          "critical",
        );
      }
    });

    if (data.risks.wildfire_risk >= 0.5) {
      addLog(
        `Extreme dryness index detected. Forest monitoring crew warned for high fire potential.`,
        "warning",
      );
    }
    if (data.risks.drought_risk >= 0.5) {
      addLog(
        `Moisture deficit index elevated. Local crop warning active.`,
        "warning",
      );
    }

    dispatchLogsBox.scrollTop = dispatchLogsBox.scrollHeight;

    // Results Card animation
    results.classList.remove("hidden");
    requestAnimationFrame(() => {
      results.classList.add("is-visible");
      // Force Leaflet sizing correction since it was initialized in a hidden div
      setTimeout(() => {
        if (mapInstance) {
          mapInstance.invalidateSize();
        }
      }, 150);
    });

    resultStatus.innerText = "Climate analysis completed";
    resultSummary.innerText =
      "Live weather and risk analysis generated successfully.";
    statusPill.innerText = "Analysis Complete";
  } catch (error) {
    console.error(error);
    loading.classList.add("hidden");
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze Climate Risk";

    showMessage("Backend server is not running.", "is-error");
  }
}

function clearResults() {
  document.getElementById("city").value = "";

  document.getElementById("state").value = "";

  document.getElementById("country").value = "";

  document.getElementById("results").classList.add("hidden");

  document.getElementById("alert-box").classList.add("hidden");

  document.getElementById("message-box").classList.add("hidden");
}

// Handle alert subscription simulation
document.addEventListener("DOMContentLoaded", () => {
  const subForm = document.getElementById("subscribe-form");
  if (subForm) {
    subForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const successMsg = document.getElementById("subscribe-success");
      successMsg.classList.remove("hidden");
      document.getElementById("subscribe-email").value = "";

      // Add a entry to logs
      const dispatchLogsBox = document.getElementById("dispatch-logs-box");
      if (dispatchLogsBox) {
        const timeStr = new Date().toLocaleTimeString();
        const entry = document.createElement("div");
        entry.className = "log-entry success";
        entry.innerHTML = `[${timeStr}] <strong>SUBSCRIBER:</strong> Stream registered for simulated notifications.`;
        dispatchLogsBox.appendChild(entry);
        dispatchLogsBox.scrollTop = dispatchLogsBox.scrollHeight;
      }

      setTimeout(() => {
        successMsg.classList.add("hidden");
      }, 4000);
    });
  }
});
window.useCurrentLocation = async function () {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async function (position) {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;

      try {
        const reverseGeocodeUrl =
          window.location.hostname === "127.0.0.1" ||
          window.location.hostname === "localhost"
            ? "http://127.0.0.1:5000/reverse-geocode"
            : window.location.origin + "/reverse-geocode";

        const response = await fetch(reverseGeocodeUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            latitude: latitude,
            longitude: longitude,
          }),
        });

        const data = await response.json();

        if (!data.success) {
          alert(data.message || "Unable to detect location.");
          return;
        }

        document.getElementById("city").value = data.city || "";
        document.getElementById("state").value = data.state || "";
        document.getElementById("country").value = data.country || "";

        getWeatherData();
      } catch (error) {
        console.error(error);
        alert("Unable to detect location.");
      }
    },
    function () {
      alert("Location permission denied.");
    },
  );
};
