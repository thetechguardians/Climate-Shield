async function getWeatherData(){

    const city =
        document.getElementById("city").value;

    const state =
        document.getElementById("state").value;

    const country =
        document.getElementById("country").value;

    const loading =
        document.getElementById("loading");

    const weatherCard =
        document.getElementById("weather-card");

    const alertBox =
        document.getElementById("alert-box");

    // =====================================
    // VALIDATION
    // =====================================

    if(
        city.trim() === "" ||
        state.trim() === "" ||
        country.trim() === ""
    ){

        alert("Please fill all fields.");
        return;
    }

    // =====================================
    // SHOW LOADING
    // =====================================

    loading.classList.remove("hidden");

    weatherCard.classList.add("hidden");

    try{

        // =====================================
        // FETCH DATA FROM PYTHON BACKEND
        // =====================================

        const response = await fetch(

            "http://127.0.0.1:5000/weather",

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

        const data = await response.json();

        loading.classList.add("hidden");

        // =====================================
        // ERROR HANDLING
        // =====================================

        if(!data.success){

            alert(data.message);
            return;
        }

        // =====================================
        // DISPLAY WEATHER DATA
        // =====================================

        document.getElementById("location").innerText =

            `${data.location.city},
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

        // =====================================
        // DISPLAY RISK SCORES
        // =====================================

        document.getElementById("flood-risk").innerText =

            data.risks.flood_risk;

        document.getElementById("heat-risk").innerText =

            data.risks.heat_risk;

        // =====================================
        // DISPLAY ALERTS
        // =====================================

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

        // =====================================
        // ALERT COLORS
        // =====================================

        if(

            data.alerts.includes(
                "⚠ Flood Risk Detected"
            )

            ||

            data.alerts.includes(
                "☀ Heatwave Risk Detected"
            )

        ){

            alertBox.classList.add("alert-danger");

            alertBox.classList.remove("alert-warning");

        }else{

            alertBox.classList.add("alert-warning");

            alertBox.classList.remove("alert-danger");
        }

        // =====================================
        // SHOW WEATHER CARD
        // =====================================

        weatherCard.classList.remove("hidden");

    }catch(error){

        console.log(error);

        loading.classList.add("hidden");

        alert(
            "Backend server is not running."
        );
    }
}