const API_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000/weather"
    : window.location.origin + "/weather";

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

      body: JSON.stringify({
        city,
        state,
        country,
      }),
    });

    const data = await response.json();

    loading.classList.add("hidden");

    if (!data.success) {
      showMessage(data.message || "Location not found.", "is-error");

      return;
    }

    hideMessage();

    saveRecentSearch(city, state, country);

    document.getElementById("location").innerText = `${data.location.city},
             ${data.location.state},
             ${data.location.country}`;

    document.getElementById("temperature").innerText =
      `${data.weather.temperature} °C`;

    document.getElementById("humidity").innerText =
      `${data.weather.humidity} %`;

    document.getElementById("rainfall").innerText =
      `${data.weather.rainfall} mm`;

    document.getElementById("wind").innerText =
      `${data.weather.wind_speed} km/h`;

    document.getElementById("flood-risk").innerText = data.risks.flood_risk;

    document.getElementById("heat-risk").innerText = data.risks.heat_risk;

    let alertsHTML = "";

    data.alerts.forEach((alertMessage) => {
      alertsHTML += `

                <div class="notification">

                    ${alertMessage}

                </div>

            `;
    });

    alertBox.innerHTML = alertsHTML;

    alertBox.classList.remove("hidden");

    resultStatus.innerText = "Climate analysis completed";

    resultSummary.innerText =
      "Live weather and risk analysis generated successfully.";

    statusPill.innerText = "Analysis Complete";

    results.classList.remove("hidden");

    requestAnimationFrame(() => {
      results.classList.add("is-visible");
    });
  } catch (error) {
    console.error(error);

    loading.classList.add("hidden");

    showMessage("Backend server is not running.", "is-error");
  }
}
function saveRecentSearch(city, state, country) {
  const newSearch = {
    city,
    state,
    country,
  };

  let searches = JSON.parse(localStorage.getItem("recentSearches")) || [];

  searches = searches.filter(
    (search) =>
      !(
        search.city === city &&
        search.state === state &&
        search.country === country
      ),
  );

  searches.unshift(newSearch);

  searches = searches.slice(0, 5);

  localStorage.setItem("recentSearches", JSON.stringify(searches));

  displayRecentSearches();
}

function displayRecentSearches() {
  const container = document.getElementById("recent-search-list");

  container.innerHTML = "";

  const searches = JSON.parse(localStorage.getItem("recentSearches")) || [];

  searches.forEach((search) => {
    const button = document.createElement("button");

    button.className = "search-chip";

    button.innerText = `${search.city}`;

    button.onclick = () => {
      document.getElementById("city").value = search.city;

      document.getElementById("state").value = search.state;

      document.getElementById("country").value = search.country;

      getWeatherData();
    };

    container.appendChild(button);
  });
}

document.getElementById("clear-history-btn").addEventListener("click", () => {
  localStorage.removeItem("recentSearches");

  displayRecentSearches();
});

displayRecentSearches();

const toggleHistoryBtn = document.getElementById("toggle-history-btn");

const recentSearchWrapper = document.getElementById("recent-search-wrapper");

toggleHistoryBtn.addEventListener("click", () => {
  recentSearchWrapper.classList.toggle("show-history");

  if (recentSearchWrapper.classList.contains("show-history")) {
    toggleHistoryBtn.innerText = "▲ Hide Recent Searches";
  } else {
    toggleHistoryBtn.innerText = "▼ Recent Searches";
  }
});
