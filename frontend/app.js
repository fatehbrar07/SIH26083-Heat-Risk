// SIH26083 Dashboard & Spatial Risk Logic

let map, geojsonLayer;
let currentLang = 'en';
let forecastChartInstance = null;
let currentAdvisoryData = null;
let selectedWardId = 'DEL-W01';

// Preset Scenarios
const PRESET_SCENARIOS = {
    scenario_a_dry_heat: { temp: 40.0, rh: 20.0, wind: 3.5, solar: 650 },
    scenario_b_humid_heat: { temp: 40.0, rh: 70.0, wind: 1.0, solar: 650 },
    scenario_c_delhi_2024_heatwave: { temp: 44.5, rh: 42.0, wind: 2.2, solar: 820 }
};

document.addEventListener("DOMContentLoaded", () => {
    initMap();
    initChart();
    updateControls();
    fetchLiveForecast();
});

function initMap() {
    map = L.map('map').setView([28.640, 77.160], 11);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);
}

function updateControls() {
    const temp = parseFloat(document.getElementById('temp-slider').value);
    const rh = parseFloat(document.getElementById('rh-slider').value);
    const wind = parseFloat(document.getElementById('wind-slider').value);
    const solar = parseFloat(document.getElementById('solar-slider').value);

    document.getElementById('temp-val').innerText = `${temp.toFixed(1)} °C`;
    document.getElementById('rh-val').innerText = `${rh.toFixed(0)} %`;
    document.getElementById('wind-val').innerText = `${wind.toFixed(1)} m/s`;
    document.getElementById('solar-val').innerText = `${solar.toFixed(0)} W/m²`;

    fetchCalculations(temp, rh, wind, solar);
    updateMapRisk(temp, rh, wind, solar);
    fetchAdvisories(temp, rh, wind, solar);
}

function loadScenario(scenarioKey) {
    const s = PRESET_SCENARIOS[scenarioKey];
    if (!s) return;

    document.getElementById('temp-slider').value = s.temp;
    document.getElementById('rh-slider').value = s.rh;
    document.getElementById('wind-slider').value = s.wind;
    document.getElementById('solar-slider').value = s.solar;

    updateControls();
}

async function fetchCalculations(temp, rh, wind, solar) {
    try {
        const res = await fetch(`/api/v1/thermal/current?temp_c=${temp}&rh_pct=${rh}&wind_speed_ms=${wind}&solar_radiation_w_m2=${solar}`);
        const data = await res.json();

        // Update UTCI
        document.getElementById('utci-display').innerText = data.utci.value_c.toFixed(1);
        const utciTag = document.getElementById('utci-tag');
        utciTag.innerText = data.utci.category;
        utciTag.style.backgroundColor = data.utci.color;
        utciTag.style.color = '#ffffff';

        // Update WBGT
        document.getElementById('wbgt-display').innerText = data.wbgt.value_c.toFixed(1);
        const wbgtTag = document.getElementById('wbgt-tag');
        wbgtTag.innerText = data.wbgt.category;
        wbgtTag.style.backgroundColor = data.wbgt.color;
        wbgtTag.style.color = '#ffffff';

        // Update Heat Index
        document.getElementById('hi-display').innerText = data.heat_index.value_c.toFixed(1);
        const hiTag = document.getElementById('hi-tag');
        hiTag.innerText = data.heat_index.category;
        hiTag.style.backgroundColor = data.heat_index.color;
        hiTag.style.color = '#ffffff';

        // Fetch Peak Ward Risk
        const riskRes = await fetch(`/api/v1/risk/current?ward_id=${selectedWardId}&temp_c=${temp}&rh_pct=${rh}&wind_speed_ms=${wind}&solar_radiation_w_m2=${solar}`);
        const riskData = await riskRes.json();
        
        document.getElementById('peak-risk-display').innerText = riskData.risk_score.toFixed(1);
        const riskTag = document.getElementById('peak-risk-tag');
        riskTag.innerText = riskData.risk_band;
        riskTag.style.backgroundColor = riskData.risk_color;
        riskTag.style.color = '#ffffff';

        // Update Inspector
        document.getElementById('inspector-ward-name').innerText = riskData.ward_name;
        document.getElementById('inspector-hvi').innerText = `${riskData.vulnerability_score.toFixed(1)} / 100`;
        document.getElementById('inspector-action').innerText = riskData.action_priority;

        if (riskData.demographic_context) {
            document.getElementById('inspector-workers').innerText = `${riskData.demographic_context.outdoor_worker_share_pct}%`;
            document.getElementById('inspector-elderly').innerText = `${riskData.demographic_context.elderly_share_pct}%`;
            document.getElementById('inspector-density').innerText = `${riskData.demographic_context.population_density.toLocaleString()} / km²`;
        }

    } catch (err) {
        console.error("Error fetching calculations:", err);
    }
}

async function updateMapRisk(temp, rh, wind, solar) {
    try {
        const res = await fetch(`/api/v1/map/risk?temp_c=${temp}&rh_pct=${rh}&wind_speed_ms=${wind}&solar_radiation_w_m2=${solar}`);
        const geojson = await res.json();

        if (geojsonLayer) {
            map.removeLayer(geojsonLayer);
        }

        geojsonLayer = L.geoJSON(geojson, {
            style: (feature) => ({
                fillColor: feature.properties.risk_color || '#F97316',
                weight: 2,
                opacity: 1,
                color: '#ffffff',
                fillOpacity: 0.75
            }),
            onEachFeature: (feature, layer) => {
                const p = feature.properties;
                layer.bindTooltip(`
                    <div class="font-sans text-xs">
                        <strong>${p.ward_name}</strong><br/>
                        Risk: <span style="color:${p.risk_color}; font-weight:bold;">${p.risk_band} (${p.risk_score})</span><br/>
                        UTCI: ${p.utci_c}°C | WBGT: ${p.wbgt_c}°C<br/>
                        HVI Vulnerability: ${p.vulnerability_score}
                    </div>
                `, { sticky: true });

                layer.on('click', () => {
                    selectedWardId = p.ward_id;
                    updateControls();
                });
            }
        }).addTo(map);

    } catch (err) {
        console.error("Error rendering GeoJSON map:", err);
    }
}

async function fetchAdvisories(temp, rh, wind, solar) {
    try {
        const res = await fetch(`/api/v1/advisory?ward_id=${selectedWardId}&temp_c=${temp}&rh_pct=${rh}&wind_speed_ms=${wind}&solar_radiation_w_m2=${solar}`);
        currentAdvisoryData = await res.json();
        renderAdvisories();
    } catch (err) {
        console.error("Error fetching advisories:", err);
    }
}

function renderAdvisories() {
    if (!currentAdvisoryData) return;

    const lang = currentLang;
    const munEl = document.getElementById('advisory-municipal');
    const hospEl = document.getElementById('advisory-hospital');
    const citEl = document.getElementById('advisory-citizen');

    const munList = currentAdvisoryData.municipal_playbook[lang === 'hi' ? 'hindi' : 'english'] || [];
    const hospList = currentAdvisoryData.healthcare_hospital_playbook[lang === 'hi' ? 'hindi' : 'english'] || [];
    const citList = currentAdvisoryData.public_citizen_advisory[lang === 'hi' ? 'hindi' : 'english'] || [];

    munEl.innerHTML = munList.map(item => `<li>${item}</li>`).join('');
    hospEl.innerHTML = hospList.map(item => `<li>${item}</li>`).join('');
    citEl.innerHTML = citList.map(item => `<li>${item}</li>`).join('');
}

function toggleLang(lang) {
    currentLang = lang;
    document.getElementById('lang-en-btn').className = lang === 'en' ? 'px-3 py-1 bg-orange-600 text-white text-xs rounded font-bold' : 'px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded font-bold hover:bg-slate-700';
    document.getElementById('lang-hi-btn').className = lang === 'hi' ? 'px-3 py-1 bg-orange-600 text-white text-xs rounded font-bold' : 'px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded font-bold hover:bg-slate-700';
    renderAdvisories();
}

function initChart() {
    const ctx = document.getElementById('forecastChart').getContext('2d');
    forecastChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['D+1', 'D+2', 'D+3', 'D+4', 'D+5'],
            datasets: [
                {
                    label: 'Air Temp (°C)',
                    data: [39.5, 41.2, 42.8, 43.5, 41.0],
                    borderColor: '#F97316',
                    backgroundColor: 'rgba(249, 115, 22, 0.1)',
                    tension: 0.3,
                    borderWidth: 2
                },
                {
                    label: 'UTCI Stress (°C)',
                    data: [42.1, 44.8, 48.2, 49.6, 45.3],
                    borderColor: '#EF4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderDash: [5, 5],
                    tension: 0.3,
                    borderWidth: 2
                },
                {
                    label: 'WBGT (°C)',
                    data: [29.2, 31.0, 33.4, 34.2, 31.8],
                    borderColor: '#38BDF8',
                    tension: 0.3,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8', boxWidth: 12, font: { size: 10 } } }
            },
            scales: {
                x: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: '#1e293b' } },
                y: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: '#1e293b' } }
            }
        }
    });
}

async function fetchLiveForecast() {
    try {
        const res = await fetch('/api/v1/thermal/forecast?lat=28.6139&lon=77.2090');
        const data = await res.json();

        if (data.projections && forecastChartInstance) {
            const labels = data.projections.map(p => `${p.horizon}\n(${p.date.slice(5)})`);
            const temps = data.projections.map(p => p.weather.temperature_c);
            const utcis = data.projections.map(p => p.utci_c);
            const wbgts = data.projections.map(p => p.wbgt_c);

            forecastChartInstance.data.labels = labels;
            forecastChartInstance.data.datasets[0].data = temps;
            forecastChartInstance.data.datasets[1].data = utcis;
            forecastChartInstance.data.datasets[2].data = wbgts;
            forecastChartInstance.update();
        }
    } catch (err) {
        console.error("Error loading forecast chart:", err);
    }
}
