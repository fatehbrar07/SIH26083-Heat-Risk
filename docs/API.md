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
    "value_c": 30.85,
    "category": "Danger",
    "severity": "HIGH",
    "color": "#F97316",
    "work_rest_cycle": "25% Work / 75% Rest per hour under shade",
    "water_intake_hourly": "1.00 Liters / hour",
    "action": "Mandate shade breaks every 15 minutes. Pre-position ORS hydration stations.",
    "standard": "ISO 7243:2017 & NIOSH Criteria"
  },
  "heat_index": {
    "value_c": 46.2,
    "category": "Danger",
    "color": "#F97316",
    "standard": "NOAA NWS Rothfusz baseline"
  }
}
```

---

#### 3. 5-Day Thermal Projections
- **Endpoint:** `GET /api/v1/thermal/forecast`
- **Query Parameters:** `lat` (float), `lon` (float)
- **Description:** Generates forward 5-day horizon projections (D+1 to D+5) evaluating diurnal peak UTCI and WBGT indices.

---

#### 4. Ward-Level Composite Human Heat-Health Risk
- **Endpoint:** `GET /api/v1/risk/current`
- **Query Parameters:** `ward_id`, `temp_c`, `rh_pct`, `wind_speed_ms`, `solar_radiation_w_m2`, `consecutive_extreme_days`
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

---

#### 7. NIOSH Occupational Heat Advisory & Work-Rest Schedules
- **Endpoint:** `GET /api/v1/advisory/occupational`
- **Query Parameters:**
  - `temp_c` (float, default 40.0): Air temperature in °C
  - `rh_pct` (float, default 35.0): Relative humidity %
  - `wind_speed_ms` (float, default 2.5): Wind speed in m/s
  - `solar_radiation_w_m2` (float, default 650.0): Solar irradiance in W/m²
  - `workload` (string, default `moderate`): `light`, `moderate`, `heavy`, `very_heavy`
  - `sector` (string, optional): `gig_delivery`, `construction`, `agriculture`, `street_vendor`
  - `acclimatized` (bool, default `true`): Worker heat acclimatization state
- **Response:** Detailed NIOSH/ISO 7243 work-rest schedule (minutes work / minutes rest per hour), hourly hydration quota (L/hr), electrolyte requirements, shift modification recommendations, heat illness emergency protocols, and targeted sector directives.

---

#### 8. Municipal Alert Dispatch & Telegram Broadcast
- **Endpoint:** `POST /api/v1/alerts/broadcast`
- **Request Body (`application/json`):**
```json
{
  "ward_id": "DEL-W01",
  "min_risk_threshold": 55.0,
  "temperature_c": 44.0,
  "relative_humidity_pct": 45.0,
  "wind_speed_ms": 2.0,
  "solar_radiation_w_m2": 750.0,
  "consecutive_extreme_days": 2,
  "channel": "telegram",
  "language": "both",
  "simulate": true
}
```
- **Response:** Broadcast confirmation detailing broadcast ID, list of alerted wards, triggered administrative actions (e.g. `ACTIVATE_COOLING_CENTERS`, `HALT_OUTDOOR_LABOR_11_TO_16`), delivery audit, and HTML bulletin payloads.

---

#### 9. Historical Heatwave Hindcast Catalog
- **Endpoint:** `GET /api/v1/hindcast/events`
- **Description:** Lists available historical heatwave benchmark events for lead-time replay and validation.

---

#### 10. Historical Heatwave Lead-Time Hindcast Replay
- **Endpoint:** `GET /api/v1/hindcast/replay`
- **Query Parameters:**
  - `event_id` (string, default `delhi_june_2024`): Historical event (`delhi_june_2024`, `ahmedabad_may_2010`, `delhi_may_2022`)
  - `ward_id` (string, default `DEL-W01`): Target ward for socio-demographic vulnerability pairing
- **Description:** Simulates the 5-day lead-time progression (D-5 to D-Day) proving 72h-120h early warning elevation before peak human thermal crisis.
