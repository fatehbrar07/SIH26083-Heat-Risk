# REST API Reference & Integration Guide

## SIH26083 Extreme Heatwave Risk Engine API (v1)

Base URL: `http://localhost:8000`  
OpenAPI Interactive Docs: `http://localhost:8000/docs`  
ReDoc Reference: `http://localhost:8000/redoc`

---

### Core Endpoints

#### 1. System Health & Source Status
- **Endpoint:** `GET /health`
- **Description:** Returns real-time connectivity and status of Tier-1 meteorological and demographic data sources.
- **Sample Response:**
```json
{
  "status": "healthy",
  "service": "SIH26083 Heatwave Risk Engine",
  "version": "1.0.0",
  "tier_1_sources": {
    "nasa_power_api": "Accessible (Public REST, MERRA-2 baseline)",
    "open_meteo_api": "Accessible (Public REST, 5-day NWP)",
    "census_2011_pca": "Loaded (Local Ward Baseline)",
    "utci_wbgt_physics": "Operational (WMO / ISO 7243 models)"
  },
  "timestamp": 1725540000.0
}
```

---

#### 2. Live / Calculated Thermal Indices
- **Endpoint:** `GET /api/v1/thermal/current`
- **Query Parameters:**
  - `temp_c` (float, default 40.0): 2m dry-bulb air temperature (°C)
  - `rh_pct` (float, default 35.0): Relative humidity (0-100%)
  - `wind_speed_ms` (float, default 2.5): Wind speed at 2m (m/s)
  - `solar_radiation_w_m2` (float, default 650.0): Global horizontal solar irradiance (W/m²)
- **Sample Response:**
```json
{
  "input_weather": {
    "air_temperature_c": 40.0,
    "relative_humidity_pct": 35.0,
    "wind_speed_ms": 2.5,
    "solar_radiation_w_m2": 650.0
  },
  "utci": {
    "value_c": 44.25,
    "category": "Very Strong Heat Stress",
    "color": "#EF4444",
    "health_risk": "Severe hyperthermia risk; heavy sweat loss, immediate cooling needed.",
    "standard": "Universal Thermal Climate Index (WMO / Fiala model)"
  },
  "wbgt": {
    "value_c": 30.82,
    "category": "High Occupational Stress (30.0 - 32.0°C)",
    "color": "#F97316",
    "work_rest_cycle": "25% Work / 75% Rest per hour under shade",
    "water_intake_liters_per_hr": 1.0,
    "standard": "ISO 7243:2017 & NIOSH Criteria"
  },
  "heat_index": {
    "value_c": 49.3,
    "category": "Danger",
    "color": "#F97316",
    "standard": "NOAA NWS Rothfusz baseline"
  }
}
```

---

#### 3. 5-Day Forward Predictive Thermal Projections
- **Endpoint:** `GET /api/v1/thermal/forecast`
- **Query Parameters:**
  - `lat` (float, default 28.6139)
  - `lon` (float, default 77.2090)
- **Description:** Evaluates 5-day forward hourly Numerical Weather Prediction data from Open-Meteo and projects daily peak UTCI, WBGT, and Heat Index trajectories.

---

#### 4. Ward-Level Composite Relative Risk
- **Endpoint:** `GET /api/v1/risk/current`
- **Query Parameters:**
  - `ward_id` (string, e.g., `DEL-W01`): Target administrative ward
  - `temp_c`, `rh_pct`, `wind_speed_ms`, `solar_radiation_w_m2`, `consecutive_extreme_days`
- **Sample Response:**
```json
{
  "ward_id": "DEL-W01",
  "ward_name": "Seelampur (Shahdara North)",
  "risk_score": 82.5,
  "risk_band": "Very High",
  "risk_color": "#EF4444",
  "action_priority": "Immediate Emergency Heat Intervention: Halt outdoor work, open cooling shelters.",
  "hazard_score": 86.5,
  "vulnerability_score": 76.5,
  "thermal_metrics": { ... },
  "duration_multiplier_applied": 1.0,
  "disclaimer": "Prototype relative risk estimate — not a clinical or mortality forecast."
}
```

---

#### 5. GIS Enriched Risk Layer
- **Endpoint:** `GET /api/v1/map/risk`
- **Query Parameters:** Environmental inputs (`temp_c`, `rh_pct`, etc.)
- **Response:** Standard GeoJSON `FeatureCollection` with injected risk properties for direct rendering in MapLibre / Leaflet.js.

---

#### 6. Action-Triggered Bilingual Advisories
- **Endpoint:** `GET /api/v1/advisory`
- **Query Parameters:** `ward_id`, `temp_c`, `rh_pct`, etc.
- **Response:** Structured municipal administration, hospital emergency, and citizen advisories in English and Hindi.
