# ☀️ SIH26083 — Extreme Heatwave Early Warning & Human Thermal Stress Index

[![FastAPI](https://img.shields.io/badge/API-FastAPI%200.110-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-11%20Passed-brightgreen.svg)]()
[![SIH Category](https://img.shields.io/badge/SIH2026-Disaster%20Management-orange.svg)]()

> **"What the weather will do to human health"** rather than merely **"what the temperature will be."**

---

## 📌 Problem Overview & The Core Paradigm Shift

Official Problem Statement: **SIH26083**  
Organization: **Ministry of Earth Sciences (MoES) / National Centre for Medium Range Weather Forecasting (NCMRWF)**  
Theme: **Disaster Management** | Category: **Software**

### ❌ Why Ambient Temperature ($T2M$) Alone is Fundamentally Insufficient
Conventional municipal heat warnings rely almost exclusively on dry-bulb air temperature ($T2M \ge 40^\circ\text{C}$ or $+4.5^\circ\text{C}$ above normal). This meteorological framing has a fatal blind spot: **human physiological thermoregulation depends entirely on the atmospheric capacity for evaporative cooling (sweating)**.

| Atmospheric Condition | Air Temp | Rel. Humidity | Solar Rad. | Physiological Consequence (UTCI / WBGT) | Municipal Consequence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Scenario A: Dry Heat** (North-West Desert Winds) | **$40.0^\circ\text{C}$** | 20% | 650 W/m² | **WBGT: $28.9^\circ\text{C}$** (Moderate / 50% work-rest cycle) | Manageable with basic hydration & rest breaks. |
| **Scenario B: Lethal Humid Heat** (Monsoon Transition) | **$40.0^\circ\text{C}$** | 70% | 650 W/m² | **WBGT: $38.0^\circ\text{C}$** (Extreme Danger / Evaporative Sweating Fails) | **Acute hyperthermia and fatal heatstroke within 2 hours of outdoor exposure.** |

The **SIH26083 Human Thermal Risk Engine** bridges this gap by calculating multi-variable biometeorological indices and overlaying them onto hyper-local socio-demographic vulnerability with a **3–5 day predictive anticipation window**.

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL TIER-1 DATA SOURCES                  │
│  ┌─────────────────────────┐              ┌──────────────────────────┐ │
│  │ NASA POWER (LaRC)       │              │ Open-Meteo NWP Forecast  │ │
│  │ 40-Yr MERRA-2 Baseline  │              │ 5-Day Hourly (T,RH,WS,GHI│ │
│  └────────────┬────────────┘              └─────────────┬────────────┘ │
└───────────────┼─────────────────────────────────────────┼──────────────┘
                │                                         │
┌───────────────┼─────────────────────────────────────────┼──────────────┐
│               ▼                                         ▼              │
│       ┌────────────────────────────────────────────────────────┐       │
│       │             Data Ingestion & In-Memory Cache           │       │
│       └───────────────────────────┬────────────────────────────┘       │
│                                   │                                    │
│   ┌───────────────────────────────┴────────────────────────────────┐   │
│   │                    CORE COMPUTATION ENGINES                    │   │
│   │  ┌────────────────────────┐       ┌────────────────────────┐   │   │
│   │  │  Thermal Stress Engine │       │  Vulnerability Engine  │   │   │
│   │  │  - UTCI (Fiala Model)  │       │  - Ward HVI (Census)   │   │   │
│   │  │  - WBGT (ISO 7243)     │       │  - Demographic Weights │   │   │
│   │  │  - NOAA Heat Index     │       │  - Density / Informal  │   │   │
│   │  └───────────┬────────────┘       └───────────┬────────────┘   │   │
│   │              │                                │                │   │
│   │              └───────────────┬────────────────┘                │   │
│   │                              ▼                                 │   │
│   │                  ┌────────────────────────┐                    │   │
│   │                  │  Composite Risk Engine │                    │   │
│   │                  │  (Hazard × HVI × Dur)  │                    │   │
│   │                  └───────────┬────────────┘                    │   │
│   └──────────────────────────────┼─────────────────────────────────┘   │
│                                  │                                     │
│   ┌──────────────────────────────┼─────────────────────────────────┐   │
│   │  DELIVERY & GIS LAYER        ▼                                 │   │
│   │  ┌──────────────────────────────────────────────────────────┐  │   │
│   │  │ FastAPI REST Endpoints (/thermal, /risk, /map/risk, /adv)│  │   │
│   │  └───────────────────────────┬──────────────────────────────┘  │   │
│   │                              │                                 │   │
│   │  ┌───────────────────────────┴──────────────────────────────┐  │   │
│   │  │ Interactive Web Dashboard (Leaflet GIS + Chart.js NWP)   │  │   │
│   │  └──────────────────────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Scientific Foundations & Methodology

### 1. Universal Thermal Climate Index (UTCI)
Derived from the multi-node Fiala human thermoregulatory model parameterized by Bröde et al. (2012) and the European COST Action 730 / WMO. It accounts for:
- 2m dry-bulb air temperature ($T_a$)
- Relative humidity / Water vapor pressure ($e_{hPa}$)
- 10m wind speed ($v_{10m}$)
- Mean Radiant Temperature ($\bar{T}_{mrt}$) calculated from Global Horizontal Irradiance ($GHI$)

### 2. Wet-Bulb Globe Temperature (WBGT) — ISO 7243:2017 & NIOSH
Standard outdoor occupational stress formulation:
$$\text{WBGT}_{\text{outdoor}} = 0.7\,T_{\text{nw}} + 0.2\,T_{\text{g}} + 0.1\,T_{\text{a}}$$
Provides actionable work-rest schedules for construction, gig, and agricultural workers.

### 3. Heat Vulnerability Index (HVI)
Computes ward-level socio-demographic susceptibility using Census of India 2011 baseline data:
$$\text{HVI} = w_{\text{elderly}}\cdot E + w_{\text{workers}}\cdot W + w_{\text{density}}\cdot D + w_{\text{informal}}\cdot I + w_{\text{children}}\cdot C$$
*(Weights calibrated to published epidemiological heat vulnerability literature in Indian cities).*

### 4. Composite Relative Heat-Health Risk (0–100)
$$\text{Relative Risk} = \min\left(100, (0.60 \cdot \text{Hazard Score} + 0.40 \cdot \text{HVI Score}) \times \text{Duration Multiplier}\right)$$
- Multi-day duration compounding adds $1.10\times$ (Day 2), $1.20\times$ (Day 3), and $1.30\times$ (Day 4+) for persistent extreme heatwaves.

---

## 📡 Tier-1 Open Data Ingestion Pipeline

| Source Name | Data Role | Access Method | Key / Cost | Status |
| :--- | :--- | :--- | :--- | :--- |
| **NASA POWER API (LaRC)** | 40-Year Climatological Baseline & Percentile Normals (MERRA-2) | REST (`power.larc.nasa.gov`) | Public / ₹0 | **Verified Live** |
| **Open-Meteo API** | 5-Day Hourly High-Resolution Forecast ($T, RH, WS, GHI$) | REST (`api.open-meteo.com`) | Public / ₹0 | **Verified Live** |
| **Census of India 2011 PCA** | Ward Demographic Indicators (Elderly, Workers, Slums) | Open Data Archive | Public / ₹0 | **Loaded** |

---

## 🚀 Quick Start & Installation

### Local Development
```bash
# 1. Clone repository
git clone https://github.com/fatehbrar07/SIH26083-Heat-Risk.git
cd SIH26083-Heat-Risk

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment config
cp .env.example .env

# 4. Run automated test suite
PYTHONPATH=. pytest backend/tests/

# 5. Launch web application & API
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the interactive dashboard at **`http://localhost:8000`** and OpenAPI documentation at **`http://localhost:8000/docs`**.

### Run with Docker Compose
```bash
docker-compose up --build -d
```

---

## 🧪 Benchmark Verification Scripts

Run standalone CLI utilities to verify the pipeline:
```bash
# 1. Verify Tier-1 Weather Ingestion (NASA POWER & Open-Meteo)
PYTHONPATH=. python3 scripts/fetch_weather.py

# 2. Benchmark Thermal Stress (UTCI vs. WBGT vs. Heat Index)
PYTHONPATH=. python3 scripts/calculate_thermal.py

# 3. Inspect Ward Heat Vulnerability Index (HVI)
PYTHONPATH=. python3 scripts/build_vulnerability.py
```

---

## 🌐 API Endpoints Reference

| HTTP Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health check and Tier-1 connectivity status |
| `GET` | `/api/v1/locations` | List supported municipal wards and coordinates |
| `GET` | `/api/v1/weather/current` | Observed / current meteorological conditions |
| `GET` | `/api/v1/weather/forecast` | 5-day hourly NWP ensemble predictions |
| `GET` | `/api/v1/thermal/current` | Instant UTCI, WBGT, and NOAA Heat Index |
| `GET` | `/api/v1/thermal/forecast` | 5-day predictive forward thermal stress trajectory |
| `GET` | `/api/v1/vulnerability` | Ward demographic vulnerability (HVI) scores |
| `GET` | `/api/v1/risk/current` | Composite ward relative risk score & NDMA band |
| `GET` | `/api/v1/risk/forecast` | 5-day predictive risk trajectory for a selected ward |
| `GET` | `/api/v1/map/risk` | Enriched GeoJSON layer for Leaflet/MapLibre mapping |
| `GET` | `/api/v1/advisory` | Action-triggered bilingual advisories (English & Hindi) |
| `GET` | `/api/v1/sources` | Complete audit provenance & Tier status matrix |
| `GET` | `/api/v1/methodology` | Mathematical formulas and weighting documentation |

---

## ⚖️ Honest Limitations & Scientific Boundaries

1. **Relative Risk vs. Clinical Counts:** The prototype outputs **Relative Heat-Health Risk (0–100)** and NDMA-aligned risk bands. It strictly avoids claiming exact mortality numbers or exact hospital admissions due to the lack of real-time clinical health data feeds.
2. **Spatial Risk Attribution:** Gridded meteorological forecasts ($\sim 11\text{km}$ resolution) are spatially attributed across administrative ward polygons and combined with micro-demographic vulnerability. We do **not** claim that the raw weather forecast itself has single-building meter-level meteorological resolution.
3. **Census 2011 Baseline:** Demographic indicators are grounded in Census of India 2011 PCA data and serve as baseline vulnerability weights.

---

## 📚 Key References
- **ISO 7243:2017:** *Ergonomics of the thermal environment — Assessment of heat stress using the WBGT index.*
- **Bröde et al. (2012):** *Deriving the operational procedure for the Universal Thermal Climate Index (UTCI).*
- **NDMA (2024):** *National Guidelines for Preparation of Action Plan - Prevention and Management of Heat Wave.*
- **NCDC / NPCCHH (2024):** *National Action Plan for Heat-Related Illnesses.*
- **Azhar et al. (2014) PLoS ONE:** *Heat-Related Mortality in India: Excess All-Cause Mortality Associated with the 2010 Ahmedabad Heat Wave.*

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
