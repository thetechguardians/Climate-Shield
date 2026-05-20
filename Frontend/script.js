document.addEventListener('DOMContentLoaded', () => {

    let map;

    const markers = {};

    const alerts = [];

    const MAX_ALERTS = 20;

    /* DOM */

    const alertContainer =
        document.getElementById('alert-container');

    const loadingAlerts =
        document.getElementById('loading-alerts');

    const statCritical =
        document.getElementById('stat-critical');

    const statTotal =
        document.getElementById('stat-total');

    const alertBadge =
        document.getElementById('alert-badge');

    const lastUpdate =
        document.getElementById('last-update');

    const searchForm =
        document.getElementById('search-form');

    const citySearch =
        document.getElementById('city-search');

    const searchBtn =
        document.getElementById('search-btn');

    const searchError =
        document.getElementById('search-error');

    const errorText =
        document.getElementById('error-text');

    /* DATA */

    const severities = [

        {
            level: 'Critical',
            colorHex: '#ef4444',
            borderClass: 'border-red-500/30',
            textClass: 'text-red-400',
            bgClass: 'bg-red-500/20'
        },

        {
            level: 'High',
            colorHex: '#f97316',
            borderClass: 'border-orange-500/30',
            textClass: 'text-orange-400',
            bgClass: 'bg-orange-500/20'
        },

        {
            level: 'Medium',
            colorHex: '#eab308',
            borderClass: 'border-yellow-500/30',
            textClass: 'text-yellow-400',
            bgClass: 'bg-yellow-500/20'
        }
    ];

    const eventTypes = [

        {
            type: 'Flood Warning',
            icon: '🌊'
        },

        {
            type: 'Heatwave Alert',
            icon: '🔥'
        },

        {
            type: 'Hurricane Watch',
            icon: '🌀'
        }
    ];

    const mockLocations = [

        {
            name: "Mumbai, IND",
            lat: 19.0760,
            lng: 72.8777
        },

        {
            name: "Tokyo, JPN",
            lat: 35.6762,
            lng: 139.6503
        },

        {
            name: "Houston, USA",
            lat: 29.7604,
            lng: -95.3698
        },

        {
            name: "Manila, PHL",
            lat: 14.5995,
            lng: 120.9842
        },

        {
            name: "Miami, USA",
            lat: 25.7617,
            lng: -80.1918
        }
    ];

    /* LAZY LEAFLET */

    async function loadLeafletAssets() {

        if (!document.getElementById('leaflet-css')) {

            const leafletCSS =
                document.createElement('link');

            leafletCSS.id = 'leaflet-css';

            leafletCSS.rel = 'stylesheet';

            leafletCSS.href =
                'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';

            document.head.appendChild(leafletCSS);
        }

        if (!window.L) {

            await new Promise((resolve) => {

                const script =
                    document.createElement('script');

                script.src =
                    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';

                script.onload = resolve;

                document.body.appendChild(script);
            });
        }
    }

    /* LOAD MAP */

    const loadMapBtn =
        document.getElementById('load-map-btn');

    loadMapBtn?.addEventListener(
        'click',
        async () => {

            loadMapBtn.disabled = true;

            loadMapBtn.textContent =
                'Loading Map...';

            await loadLeafletAssets();

            const mapContainer =
                document.getElementById('map-container');

            mapContainer.innerHTML = `
                <div
                    id="map"
                    class="w-full h-full">
                </div>
            `;

            requestAnimationFrame(initMap);
        }
    );

    /* INIT MAP */

    function initMap() {

        map = L.map('map', {

            zoomControl: false,

            preferCanvas: true,

            fadeAnimation: false,

            zoomAnimation: false,

            markerZoomAnimation: false

        }).setView([20, 0], 3);

        L.tileLayer(
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',

            {
                attribution:
                    '&copy; OpenStreetMap',

                maxZoom: 18
            }

        ).addTo(map);

        L.control.zoom({
            position: 'topright'
        }).addTo(map);
    }

    /* ALERT TEMPLATE */

    function createAlertCard(alert) {

        const time =
            alert.timestamp.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });

        return `
            <article
                class="
                    alert-card
                    bg-slate-900/60
                    rounded-2xl
                    p-4
                    border
                    ${alert.severity.borderClass}
                    cursor-pointer
                "

                data-lat="${alert.lat}"
                data-lng="${alert.lng}"
                data-id="${alert.id}"
            >

                <div class="flex justify-between items-start mb-3">

                    <div class="flex gap-3">

                        <div
                            class="
                                w-10 h-10
                                rounded-xl
                                ${alert.severity.bgClass}
                                flex items-center justify-center
                                text-lg
                            ">

                            ${alert.icon}

                        </div>

                        <div>

                            <h3 class="font-semibold text-sm text-white">

                                ${alert.type}

                            </h3>

                            <p class="text-xs text-slate-300 mt-1">

                                📍 ${alert.location}

                            </p>

                        </div>

                    </div>

                    <span
                        class="
                            text-[10px]
                            font-semibold
                            px-2 py-1
                            rounded-lg
                            bg-slate-950
                            border border-slate-700
                            ${alert.severity.textClass}
                        ">

                        ${alert.severity.level}

                    </span>

                </div>

                <p
                    class="
                        text-xs
                        text-slate-300
                        leading-relaxed
                    ">

                    ${alert.details}

                </p>

                <div
                    class="
                        mt-3
                        flex justify-between items-center
                        text-[10px]
                        text-slate-400
                    ">

                    <span>
                        ID: ${alert.id}
                    </span>

                    <span>
                        🕒 ${time}
                    </span>

                </div>

            </article>
        `;
    }

    /* MAP MARKERS */

    function addMarker(alert) {

        if (!map) return;

        const iconHtml =

            alert.severity.level === 'Critical'

                ? `<div class="pulse-marker"></div>`

                : `
                    <div
                        style="
                            width:14px;
                            height:14px;
                            border-radius:50%;
                            background:${alert.severity.colorHex};
                            border:2px solid white;
                        ">
                    </div>
                `;

        const icon = L.divIcon({

            className: '',

            html: iconHtml,

            iconSize: [18, 18]
        });

        const marker = L.marker(
            [alert.lat, alert.lng],
            { icon }
        ).addTo(map);

        markers[alert.id] = marker;
    }

    /* DASHBOARD */

    function updateDashboard() {

        const criticalCount =

            alerts.filter(
                alert =>
                    alert.severity.level === 'Critical'
            ).length;

        statCritical.textContent =
            criticalCount;

        statTotal.textContent =
            alerts.length;

        alertBadge.textContent =
            alerts.length;

        lastUpdate.textContent =
            `Updated: ${new Date().toLocaleTimeString()}`;
    }

    /* INJECT ALERT */

    function injectAlert(alert) {

        loadingAlerts?.remove();

        if (alerts.length >= MAX_ALERTS) {

            const oldest = alerts.pop();

            if (markers[oldest.id]) {

                map?.removeLayer(
                    markers[oldest.id]
                );

                delete markers[oldest.id];
            }

            alertContainer.lastElementChild?.remove();
        }

        alerts.unshift(alert);

        alertContainer.insertAdjacentHTML(
            'afterbegin',
            createAlertCard(alert)
        );

        addMarker(alert);

        updateDashboard();
    }

    /* SEARCH */

    searchForm.addEventListener(
        'submit',
        async (event) => {

            event.preventDefault();

            const city =
                citySearch.value.trim();

            if (!city) return;

            searchBtn.disabled = true;

            searchBtn.textContent =
                'Searching...';

            searchError.classList.add('hidden');

            try {

                const response =
                    await fetch(
                        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(city)}&format=json&limit=1`
                    );

                const data =
                    await response.json();

                if (!data.length) {

                    throw new Error(
                        'Location not found'
                    );
                }

                const location = data[0];

                injectAlert({

                    id: `ALRT-${Date.now()}`,

                    type: 'Manual Search',

                    icon: '📍',

                    severity: severities[0],

                    location:
                        location.display_name
                            .split(',')
                            .slice(0, 2)
                            .join(','),

                    lat:
                        parseFloat(location.lat),

                    lng:
                        parseFloat(location.lon),

                    timestamp: new Date(),

                    details:
                        'Manually monitored climate activity for this region.'

                });

                citySearch.value = '';

            } catch (error) {

                errorText.textContent =
                    error.message;

                searchError.classList.remove('hidden');

            } finally {

                searchBtn.disabled = false;

                searchBtn.textContent =
                    'Search';
            }
        }
    );

    /* RANDOM ALERT */

    function createRandomAlert() {

        const eventType =
            eventTypes[
            Math.floor(
                Math.random() * eventTypes.length
            )
            ];

        const severity =
            severities[
            Math.floor(
                Math.random() * severities.length
            )
            ];

        const location =
            mockLocations[
            Math.floor(
                Math.random() * mockLocations.length
            )
            ];

        injectAlert({

            id: `ALRT-${Date.now()}`,

            type: eventType.type,

            icon: eventType.icon,

            severity,

            location: location.name,

            lat:
                location.lat +
                ((Math.random() - 0.5) * 2),

            lng:
                location.lng +
                ((Math.random() - 0.5) * 2),

            timestamp: new Date(),

            details:
                'Sensor thresholds breached. Monitoring systems indicate elevated environmental risk.'
        });
    }

    requestIdleCallback(() => {

        for (let i = 0; i < 2; i++) {

            createRandomAlert();
        }

    });

    const alertInterval =
        setInterval(() => {

            if (Math.random() > 0.35) {

                createRandomAlert();
            }

        }, 12000);

    window.addEventListener(
        'beforeunload',
        () => {

            clearInterval(alertInterval);
        }
    );
});