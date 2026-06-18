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

const descriptions = {
  flood: {
    low: "No significant flood risk. Normal conditions.",
    moderate: "Some flood potential. Avoid low-lying areas.",
    high: "Elevated flood risk. Stay away from rivers.",
    critical: "Dangerous floods. Move to higher ground immediately.",
  },
  heat: {
    low: "Comfortable temperatures. No precautions needed.",
    moderate: "Mild heat stress. Stay hydrated.",
    high: "High heat risk. Avoid outdoor exertion.",
    critical: "Extreme heat emergency. Stay indoors.",
  },
  wildfire: {
    low: "Calm conditions. No immediate fire risk.",
    moderate: "Dry conditions. Avoid open burning.",
    high: "Elevated fire risk. Be ready to evacuate.",
    critical: "Critical fire danger. Follow evacuation orders.",
  },
  cyclone: {
    low: "Stable weather. No cyclone activity.",
    moderate: "Low-level indicators. Monitor weather bulletins.",
    high: "Significant cyclone risk. Secure loose objects.",
    critical: "Severe cyclone warning. Seek sturdy shelter.",
  },
  drought: {
    low: "Normal water supply. No drought stress.",
    moderate: "Possible drought stress. Conserve water.",
    high: "Significant drought. Restrict water use.",
    critical: "Severe drought. Comply with rationing measures.",
  },
};

const cityInput = document.getElementById("city");
const suggestionsBox = document.getElementById("city-suggestions");

if (cityInput && suggestionsBox) {
  cityInput.addEventListener("input", async () => {
      console.log("Typing:", cityInput.value);

    const query = cityInput.value.trim();
const currentQuery = query;;

    if (query.length < 2) {
      suggestionsBox.innerHTML = "";
      suggestionsBox.classList.add("hidden");
      return;
    }

    try {
      const CITY_API_URL =
        window.location.hostname === "127.0.0.1" ||
        window.location.hostname === "localhost"
          ? "http://127.0.0.1:5000/city-suggestions"
          : window.location.origin + "/city-suggestions";
      const response = await fetch(
        `${CITY_API_URL}?q=${encodeURIComponent(query)}`,
      );

      const cities = await response.json();
      if (cityInput.value.trim() !== currentQuery) {
  return;
}
      console.log("Cities:", cities);

     suggestionsBox.innerHTML = "";

if (cities.length === 0) {
  suggestionsBox.classList.add("hidden");
  return;
}

suggestionsBox.classList.remove("hidden");
suggestionsBox.classList.remove("hidden");
console.log("After remove:", suggestionsBox.className);
console.log(cities);
      cities.forEach((city) => {
        const item = document.createElement("div");

        item.className = "city-suggestion-item";

        item.textContent = [city.city, city.state, city.country]
  .filter(Boolean)
  .join(", ");

        item.addEventListener("click", () => {
          cityInput.value = city.city;
          document.getElementById("state").value = city.state;
          document.getElementById("country").value = city.country;

          suggestionsBox.innerHTML = "";
          suggestionsBox.classList.add("hidden");
        });

        suggestionsBox.appendChild(item);
      });
      console.log("Children:", suggestionsBox.children.length);
console.log(suggestionsBox.innerHTML);
    } catch (err) {
      console.error("Autocomplete Error:", err);
    }
  });
}

function getRiskLevel(score, riskType) {
  const type = riskType.toLowerCase();
  const d = descriptions[type] || descriptions.flood;

  if (score <= 0.29) return { label: "Low", cssClass: "low", desc: d.low };
  if (score <= 0.49)
    return { label: "Moderate", cssClass: "moderate", desc: d.moderate };
  if (score <= 0.69) return { label: "High", cssClass: "high", desc: d.high };
  return { label: "Critical", cssClass: "critical", desc: d.critical };
}

// ==========================================
// AI-POWERED SAFETY RECOMMENDATIONS
// ==========================================

// API key must be set by the user in a .env file or backend config
// Never hardcode API keys in frontend code!
const OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY";

async function getAIRecommendations(weatherData) {
  const recommendationsPanel = document.getElementById("recommendations-panel");
  const recommendationsList = document.getElementById("recommendations-list");

  recommendationsPanel.classList.remove("hidden");
  recommendationsList.innerHTML = `<li>🤖 Generating AI safety recommendations...</li>`;

  const prompt = `You are a climate safety expert. Based on these weather conditions:
- Temperature: ${weatherData.temperature}°C
- Humidity: ${weatherData.humidity}%
- Rainfall: ${weatherData.rainfall}mm
- Wind Speed: ${weatherData.windSpeed} km/h
- Primary Risk: ${weatherData.primaryRisk}

Give exactly 4 short practical safety precautions as a JSON array of strings.
Respond ONLY with a JSON array, no extra text, no markdown.
Example: ["tip1", "tip2", "tip3", "tip4"]`;

  try {
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "mistralai/mistral-7b-instruct",
        messages: [{ role: "user", content: prompt }]
      })
    });

    const result = await response.json();
    const text = result.choices[0].message.content.trim();
    const clean = text.replace(/```json|```/g, "").trim();
    const tips = JSON.parse(clean);

    recommendationsList.innerHTML = tips
      .map(tip => `<li>✅ ${tip}</li>`)
      .join("");

  } catch (error) {
    console.error("AI recommendation error:", error);
    // Fallback to static recommendations if AI fails
    recommendationsList.innerHTML = `
      <li>✅ Stay hydrated and monitor weather updates.</li>
      <li>✅ Avoid unnecessary outdoor activities during high risk.</li>
      <li>✅ Keep emergency supplies ready.</li>
      <li>✅ Follow local authority advisories.</li>
    `;
  }
}


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
    
    if (typeof saveRecentSearch === "function") {
      saveRecentSearch(city, state, country);
    }

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
    const floodCard = document.querySelector(".risk-card.flood");
    const floodScore = data.risks.flood_risk;
    document.getElementById("flood-risk").innerText = floodScore;
    let score = floodScore;
    let card = floodCard;
    let level = getRiskLevel(score, "flood");
    let labelEl = card.querySelector(".risk-label");
    labelEl.textContent = level.label;
    labelEl.className = "risk-label " + level.cssClass;
    card.querySelector(".risk-description").textContent = level.desc;

    const heatCard = document.querySelector(".risk-card.heat");
    const heatScore = data.risks.heat_risk;
    document.getElementById("heat-risk").innerText = heatScore;
    score = heatScore;
    card = heatCard;
    level = getRiskLevel(score, "heat");
    labelEl = card.querySelector(".risk-label");
    labelEl.textContent = level.label;
    labelEl.className = "risk-label " + level.cssClass;
    card.querySelector(".risk-description").textContent = level.desc;

    const wildfireCard = document.querySelector(".risk-card.wildfire");
    const wildfireScore = data.risks.wildfire_risk;
    document.getElementById("wildfire-risk").innerText = wildfireScore;
    score = wildfireScore;
    card = wildfireCard;
    level = getRiskLevel(score, "wildfire");
    labelEl = card.querySelector(".risk-label");
    labelEl.textContent = level.label;
    labelEl.className = "risk-label " + level.cssClass;
    card.querySelector(".risk-description").textContent = level.desc;

    const cycloneCard = document.querySelector(".risk-card.cyclone");
    const cycloneScore = data.risks.cyclone_risk;
    document.getElementById("cyclone-risk").innerText = cycloneScore;
    score = cycloneScore;
    card = cycloneCard;
    level = getRiskLevel(score, "cyclone");
    labelEl = card.querySelector(".risk-label");
    labelEl.textContent = level.label;
    labelEl.className = "risk-label " + level.cssClass;
    card.querySelector(".risk-description").textContent = level.desc;

    const droughtCard = document.querySelector(".risk-card.drought");
    const droughtScore = data.risks.drought_risk;
    document.getElementById("drought-risk").innerText = droughtScore;
    score = droughtScore;
    card = droughtCard;
    level = getRiskLevel(score, "drought");
    labelEl = card.querySelector(".risk-label");
    labelEl.textContent = level.label;
    labelEl.className = "risk-label " + level.cssClass;
    card.querySelector(".risk-description").textContent = level.desc;

    // ==========================================
    // CALL AI RECOMMENDATIONS
    // ==========================================
    const primaryRiskName = Object.entries({
      Flood: floodScore,
      Heat: heatScore,
      Wildfire: wildfireScore,
      Cyclone: cycloneScore,
      Drought: droughtScore
    }).sort((a, b) => b[1] - a[1])[0][0];

    getAIRecommendations({
      temperature: data.weather.temperature,
      humidity: data.weather.humidity,
      rainfall: data.weather.rainfall,
      windSpeed: data.weather.wind_speed,
      primaryRisk: primaryRiskName + " Risk"
    });

    // Store last analysis result so ClimateBot can use it
    window.lastAnalysisContext = {
      location: {
        city: city,
        state: state,
        country: country,
      },
      weather: {
        temperature: data.weather.temperature,
        humidity: data.weather.humidity,
        rainfall: data.weather.rainfall,
        wind_speed: data.weather.wind_speed,
      },
      risks: {
        flood_risk: data.risks.flood_risk,
        heat_risk: data.risks.heat_risk,
        wildfire_risk: data.risks.wildfire_risk,
        cyclone_risk: data.risks.cyclone_risk,
        drought_risk: data.risks.drought_risk,
      },
    };

    // Update chatbot context badge if it exists
    const badge = document.getElementById("chatbot-context-badge");
    if (badge) {
      badge.textContent = "📍 " + city + ", " + state;
      badge.style.display = "inline-block";
    }

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

      const darkTile  = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
      const lightTile = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';

      const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      let tileLayer = L.tileLayer(
        currentTheme === 'light' ? lightTile : darkTile,
        { attribution: '© OpenStreetMap © CARTO', maxZoom: 19 }
      ).addTo(mapInstance);

      window.addEventListener('themechange', function (e) {
        tileLayer.remove();
        tileLayer = L.tileLayer(
          e.detail.theme === 'light' ? lightTile : darkTile,
          { attribution: '© OpenStreetMap © CARTO', maxZoom: 19 }
        ).addTo(mapInstance);
      });
    } else {
      mapInstance.setView([lat, lon], 10);
      mapInstance.eachLayer((layer) => {
        if (layer instanceof L.Marker || layer instanceof L.Circle) {
          mapInstance.removeLayer(layer);
        }
      });
    }

    const maxRisk = Math.max(
      data.risks.flood_risk,
      data.risks.heat_risk,
      data.risks.wildfire_risk,
      data.risks.cyclone_risk,
      data.risks.drought_risk,
    );
    let circleColor = "#22c55e";
    if (maxRisk >= 0.7) {
      circleColor = "#ef4444";
    } else if (maxRisk >= 0.5) {
      circleColor = "#f59e0b";
    }

    L.circle([lat, lon], {
      color: circleColor,
      fillColor: circleColor,
      fillOpacity: 0.15,
      radius: 10000,
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
      mapInstance.once("moveend", () => {
        mapMarker.openPopup();
      });

    // Render 5-Day Forecast
    const forecastContainer = document.getElementById("forecast-cards-container");
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
      const riskMap = {
        Flood: day.risks.flood_risk,
        Heat: day.risks.heat_risk,
        Wildfire: day.risks.wildfire_risk,
        Cyclone: day.risks.cyclone_risk,
        Drought: day.risks.drought_risk,
      };

      const sortedRisks = Object.entries(riskMap).sort((a, b) => b[1] - a[1]);
      const primaryRisk = sortedRisks[0];
      const secondaryRisk = sortedRisks[1];
      const primaryCause = primaryRisk[0];
      const primaryScore = primaryRisk[1];

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
    <div class="forecast-risk-indicator ${isDanger ? "has-danger" : ""}">
        ${alertTag}
    </div>
    <div class="forecast-primary-cause">
        Primary Cause: ${primaryCause} Risk (${primaryScore.toFixed(2)})
    </div>
    <div class="forecast-secondary-cause">
        Also: ${secondaryRisk[0]} Risk (${secondaryRisk[1].toFixed(2)})
    </div>
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
      const badgeMap = {
        success: { label: "INFO", className: "badge-info", icon: "🛡️" },
        warning: { label: "WARNING", className: "badge-warning", icon: "⚠️" },
        critical: { label: "CRITICAL", className: "badge-critical", icon: "🚨" },
      };
      const config = badgeMap[tone];
      const entry = document.createElement("div");
      entry.className = `log-entry ${tone}`;
      entry.innerHTML = `
    <div class="log-header">
      <span class="log-badge ${config.className}">${config.icon} ${config.label}</span>
      <span class="log-time">${timeStr}</span>
    </div>
    <div class="log-message">${msg}</div>
  `;
      dispatchLogsBox.appendChild(entry);
    };

    addLog(`Monitoring node activated at Lat ${lat.toFixed(4)}, Lon ${lon.toFixed(4)}`, "success");
    if (data.demo_mode) {
      addLog(`OpenWeather key unconfigured/expired. Defaulting to Demo Mode simulation.`, "warning");
    }

    data.alerts.forEach((alert) => {
      if (alert.includes("✅")) {
        addLog(`No active hazards flagged. Parameters sit within safety standard threshold limit.`, "success");
      } else {
        addLog(`CRITICAL BROADCAST: ${alert} active in the target area!`, "critical");
      }
    });

    if (data.risks.wildfire_risk >= 0.5) {
      addLog(`Extreme dryness index detected. Forest monitoring crew warned for high fire potential.`, "warning");
    }
    if (data.risks.drought_risk >= 0.5) {
      addLog(`Moisture deficit index elevated. Local crop warning active.`, "warning");
    }

    dispatchLogsBox.scrollTop = dispatchLogsBox.scrollHeight;

    // Results Card animation
    results.classList.remove("hidden");
    requestAnimationFrame(() => {
      results.classList.add("is-visible");
      setTimeout(() => {
        if (mapInstance) {
          mapInstance.invalidateSize();
        }
      }, 150);
    });

    resultStatus.innerText = "Climate analysis completed";
    resultSummary.innerText = "Live weather and risk analysis generated successfully.";
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
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ latitude: latitude, longitude: longitude }),
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
    }
  );
};

document.addEventListener("DOMContentLoaded", () => {
    const typingTextElement = document.getElementById("hero-typing-text");
    if (typingTextElement) {
        const textToType = "Check flood and heat risk for any location in seconds.";
        let i = 0;
        typingTextElement.innerHTML = '<span id="typing-content"></span><span class="typewriter-cursor"></span>';
        const contentSpan = document.getElementById("typing-content");

        function typeWriter() {
            if (i < textToType.length) {
                contentSpan.innerHTML += textToType.charAt(i);
                i++;
                setTimeout(typeWriter, 40);
            } else {
                setTimeout(() => {
                    const cursor = document.querySelector('.typewriter-cursor');
                    if(cursor) cursor.style.display = 'none';
                }, 3000);
            }
        }
        setTimeout(typeWriter, 400);
    }

    const toggleBtn = document.getElementById("toggle-history-btn");
    const wrapper = document.getElementById("recent-search-wrapper");
    const clearBtn = document.getElementById("clear-history-btn");

    if (toggleBtn && wrapper) {
      toggleBtn.addEventListener("click", () => {
        wrapper.classList.toggle("show-history");
        if (wrapper.classList.contains("show-history")) {
          toggleBtn.innerText = "Recent Searches ▲";
        } else {
          toggleBtn.innerText = "Recent Searches ▼";
        }
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        localStorage.removeItem("recentSearches");
        if (typeof displayRecentSearches === "function") {
            displayRecentSearches();
        }
      });
    }

    const carouselImages = document.querySelectorAll(".hero-image-carousel .carousel-img");
    if (carouselImages.length > 0) {
        let currentImageIndex = 0;
        setInterval(() => {
            carouselImages[currentImageIndex].classList.remove("active");
            currentImageIndex = (currentImageIndex + 1) % carouselImages.length;
            carouselImages[currentImageIndex].classList.add("active");
        }, 5000);
    }

    if (typeof fetchAndRenderChart === 'function') {
        fetchAndRenderChart(20.5937, 78.9629);
    }
});

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
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

let temperatureChartInstance = null;

async function fetchAndRenderChart(lat, lon) {
    const chartUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=auto`;
    try {
        const res = await fetch(chartUrl);
        const data = await res.json();
        
        if (data.current) {
            const tempEl = document.getElementById('temperature');
            if (tempEl && (!tempEl.innerText || tempEl.innerText.trim() === "")) {
                tempEl.innerText = `${data.current.temperature_2m} °C`;
                document.getElementById('humidity').innerText = `${data.current.relative_humidity_2m} %`;
                document.getElementById('rainfall').innerText = `${data.current.precipitation} mm`;
                document.getElementById('wind').innerText = `${data.current.wind_speed_10m} km/h`;
                document.getElementById('location').innerText = 'Overall India (Default)';
                document.getElementById('flood-risk').innerText = '0.12';
                document.getElementById('heat-risk').innerText = '0.85';
            }
        }

        const dates = data.daily.time.map(d => {
            const date = new Date(d);
            return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        });
        const maxTemps = data.daily.temperature_2m_max;
        const minTemps = data.daily.temperature_2m_min;

        const ctx = document.getElementById('temperatureChart');
        if (!ctx) return;

        if (temperatureChartInstance) {
            temperatureChartInstance.destroy();
        }

        Chart.defaults.color = 'rgba(255, 255, 255, 0.7)';
        Chart.defaults.font.family = "'Poppins', sans-serif";

        temperatureChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'Max Temp (°C)',
                        data: maxTemps,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Min Temp (°C)',
                        data: minTemps,
                        borderColor: '#3b82f6',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        tension: 0.4,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: {
                    y: { grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                    x: { grid: { color: 'rgba(255, 255, 255, 0.1)' } }
                }
            }
        });
    } catch (err) {
        console.error("Error fetching chart data:", err);
    }

  function getRecentSearches() {
    return JSON.parse(localStorage.getItem("recentSearches")) || [];
  }

  function saveRecentSearch(city, state, country) {
    if (!city || !state || !country) return;
    const newSearch = { city, state, country };
    let searches = getRecentSearches();
    searches = searches.filter(
      (search) =>
        !(
          search.city.toLowerCase() === city.toLowerCase() &&
          search.state.toLowerCase() === state.toLowerCase() &&
          search.country.toLowerCase() === country.toLowerCase()
        ),
    );
    searches.unshift(newSearch);
    searches = searches.slice(0, 5);
    localStorage.setItem("recentSearches", JSON.stringify(searches));
    displayRecentSearches();
  }

  function displayRecentSearches() {
    const container = document.getElementById("recent-search-list");
    if (!container) return;
    container.innerHTML = "";
    const searches = getRecentSearches();
    searches.forEach((search) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "search-chip";
      button.innerText = search.city;
      button.addEventListener("click", () => {
        document.getElementById("city").value = search.city;
        document.getElementById("state").value = search.state;
        document.getElementById("country").value = search.country;
        getWeatherData();
      });
      container.appendChild(button);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    displayRecentSearches();
    const toggleBtn = document.getElementById("toggle-history-btn");
    const wrapper = document.getElementById("recent-search-wrapper");
    const clearBtn = document.getElementById("clear-history-btn");
    if (toggleBtn && wrapper) {
      toggleBtn.addEventListener("click", () => {
        wrapper.classList.toggle("show-history");
        if (wrapper.classList.contains("show-history")) {
          toggleBtn.innerText = "Recent Searches ▲";
        } else {
          toggleBtn.innerText = "Recent Searches ▼";
        }
      });
    }
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        localStorage.removeItem("recentSearches");
        displayRecentSearches();
      });
    }
  });
}

// Theme toggle logic is handled globally by theme.js