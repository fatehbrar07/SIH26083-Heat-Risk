# System Architecture & Engineering Specification

## SIH26083 — Extreme Heatwave Early Warning and Human Thermal Stress Index
**Ministry of Earth Sciences (MoES) / NCMRWF**

---

### 1. Executive Summary & Paradigm Shift
Traditional meteorological forecasts communicate ambient temperature ($T2M$). However, dry-bulb temperature alone fails to capture human physiological strain. A dry $40^\circ\text{C}$ air mass allows active evaporative sweating, while a humid $40^\circ\text{C}$ air mass impedes latent heat dissipation, leading to core hyperthermia and fatal heatstroke. 

The **SIH26083 Human Thermal Risk Engine** transforms raw meteorological forecasts into actionable human health risk by computing multi-variable biometeorological indices (**Universal Thermal Climate Index [UTCI]** and **ISO 7243 Wet-Bulb Globe Temperature [WBGT]**) and overlaying them onto hyper-local socio-demographic vulnerability (**Census 2011 Heat Vulnerability Index [HVI]**) with multi-day persistence compounding.

---

### 2. Architecture Diagrams (All 9 Required Specifications)

#### Diagram 1: Overall System Architecture
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

#### Diagram 2: End-to-End Data Flow
```
[External Public APIs]
       │
       ▼ (Async HTTP / TTL Caching)
[Ingestion Module] ──► Extracts: T2M (°C), RH (%), WS (m/s), Solar (W/m²)
       │
       ├──► [UTCI Calculation] ──► Fiala Polynomial Approximation ──► UTCI (°C)
       ├──► [WBGT Calculation] ──► Liljegren Psychrometric Engine ──► WBGT (°C)
       │
       ▼
[Hazard Score Generation] ──► 0 - 100 Normalized Hazard
       │
       ├──► [Demographic Overlay] ◄── Census 2011 PCA (Elderly, Workers, Slums)
       ├──► [Duration Multiplier] ◄── Consecutive Days ≥ 40°C (1.0x to 1.3x)
       │
       ▼
[Composite Relative Risk] ──► Ward Score (0-100) & NDMA Risk Band
       │
       ├──► GeoJSON Spatial Property Enrichment
       ├──► Bilingual Municipal & Hospital Playbook Triggers
       ▼
[FastAPI Response JSON & Web UI Visualization]
```

#### Diagram 3: Thermal Stress Engine
```
┌─────────────────────────────────────────────────────────────────┐
│                    METEOROLOGICAL VECTOR                        │
│   Dry-Bulb Temp (T)   Rel Humidity (RH)   Wind (WS)   Solar (GHI│
└─────────┬────────────────────┬────────────────┬────────────┬────┘
          │                    │                │            │
          ├────────────────────┼────────────────┼────────────┤
          ▼                    ▼                ▼            ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│   UTCI Engine    │ │   WBGT Engine    │ │  Heat Index Engine   │
│  - Vapor Press.  │ │  - Tw (Natural)  │ │  - Steadman /        │
│  - Tmrt Delta    │ │  - Tg (Black-Gl) │ │    Rothfusz Regress. │
│  - Brode Regress.│ │  - 0.7Tw+0.2Tg+0.1││  - Baseline Shade T  │
└─────────┬────────┘ └─────────┬────────┘ └──────────┬───────────┘
          │                    │                     │
          ▼                    ▼                     ▼
    UTCI (°C Stress)     WBGT (°C Work)        Apparent Temp (°C)
          │                    │                     │
          └───────────┬────────┘                     │
                      ▼                              ▼
          [Blended Hazard Score 0-100]       [Reference Metric]
```

#### Diagram 4: Vulnerability Engine
```
┌─────────────────────────────────────────────────────────┐
│               CENSUS OF INDIA 2011 BASELINE             │
└───────────────────────────┬─────────────────────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
[Elderly Share (60+)]  [Outdoor Laborers]  [Pop Density / Slums]
   Weight: 35%            Weight: 25%          Weight: 25%
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                            ▼ (Min-Max Normalization)
               ┌───────────────────────────┐
               │    Ward HVI Score (0-100) │
               │   - High (>70)            │
               │   - Moderate (45-69)      │
               │   - Low (<45)             │
               └───────────────────────────┘
```

#### Diagram 5: Composite Risk Engine
```
  [Physiological Hazard (0-100)]         [Ward Vulnerability (0-100)]
             (Weight: 60%)                            (Weight: 40%)
                   │                                        │
                   └───────────────────┬────────────────────┘
                                       │
                                       ▼
                       [Raw Base Risk = 0.60H + 0.40V]
                                       │
                                       ▼
                    [× Consecutive Day Multiplier (1.0 - 1.3)]
                                       │
                                       ▼
                     [Final Heat Risk Score (0 - 100)]
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
     Low Risk (<30)             Moderate (30-54)            High (55-79)
    Routine Advisory        Precautionary Alert       Work-Rest & Water Tankers
                                                                  ▼
                                                          Very High (80+)
                                                      Emergency Protocols
```

#### Diagram 6: GIS Flow & Risk Attribution
```
┌──────────────────────────┐          ┌──────────────────────────┐
│  Weather Forecast Grid   │          │  Official Ward Boundary  │
│  (0.1° / ~11km Open-Met) │          │  Polygons (GeoJSON)      │
└────────────┬─────────────┘          └────────────┬─────────────┘
             │                                     │
             └──────────────────┬──────────────────┘
                                │
                                ▼
             [Spatial Attribution & Downscaling]
             - Attribute grid weather to administrative ward
             - Compute micro-demographic HVI per ward
             - Calculate Ward Risk & NDMA Category
                                │
                                ▼
             [Enriched GeoJSON Layer Output]
             - Injected properties: risk_score, risk_color,
               utci_c, wbgt_c, demographics, action_priority
                                │
                                ▼
             [Leaflet.js Vector Choropleth Visualization]
```

#### Diagram 7: API Architecture
```
[Client Applications: Web Dashboard / SMS Gateway / Municipal Dispatch]
                               │
                               ▼ HTTP GET/POST (JSON)
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Application Gateway                     │
│  ├── /health                        ── System Health & Source Status   │
│  ├── /api/v1/locations              ── Ward metadata & coordinates     │
│  ├── /api/v1/weather/current        ── Current observed conditions     │
│  ├── /api/v1/weather/forecast       ── 5-day NWP ensemble predictions  │
│  ├── /api/v1/thermal/current        ── UTCI / WBGT / HI calculations   │
│  ├── /api/v1/thermal/forecast       ── 5-day forward thermal stress    │
│  ├── /api/v1/vulnerability          ── Ward HVI demographic scores    │
│  ├── /api/v1/risk/current           ── Instant ward composite risk     │
│  ├── /api/v1/risk/forecast          ── 5-day predictive risk trajectory│
│  ├── /api/v1/map/risk               ── GeoJSON risk choropleth layer   │
│  ├── /api/v1/advisory               ── Bilingual municipal action plans│
│  ├── /api/v1/sources                ── Provenance & Tier-1 registry    │
│  └── /api/v1/methodology            ── Equations & weighting rubric    │
└────────────────────────────────────────────────────────────────────────┘
```

#### Diagram 8: Deployment Architecture
```
┌────────────────────────────────────────────────────────┐
│                     CLIENT BROWSER                     │
│        (Leaflet Map, Interactive Sliders, Charts)      │
└───────────────────────────┬────────────────────────────┘
                            │ Port 8000 (HTTP / REST)
                            ▼
┌────────────────────────────────────────────────────────┐
│               DOCKER CONTAINER (Linux Host)            │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Uvicorn ASGI Server (Multi-Worker Async)         │  │
│  │ ┌──────────────────────────────────────────────┐ │  │
│  │ │ FastAPI Application Core                     │ │  │
│  │ │ - Async HTTP Clients (httpx)                 │ │  │
│  │ │ - In-Memory Ingestion Caches (1h - 24h TTL)  │ │  │
│  │ │ - Scientific Compute (NumPy / Pure Python)   │ │  │
│  │ └──────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS Outbound (Keyless)
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
 [NASA POWER API (LaRC)]              [Open-Meteo Weather API]
```

#### Diagram 9: SIH Requirement Traceability
```
SIH Mandatory Mandate               Implemented Module              Evidence
────────────────────────────────────────────────────────────────────────────────────────
1. Human Thermal Stress Index   ──► backend/app/thermal/       ──► UTCI & ISO 7243 WBGT
2. Weather Variables (T,RH,WS,R)──► backend/app/data_sources/  ──► Open-Meteo & NASA POWER
3. 3-5 Day Anticipation         ──► /api/v1/thermal/forecast   ──► 5-day hourly NWP horizon
4. Demographic Vulnerability    ──► backend/app/vulnerability/ ──► Census 2011 HVI Engine
5. Hyper-Local GIS Mapping      ──► backend/app/gis/           ──► Ward Risk GeoJSON + Leaflet
6. Actionable Civic Advisories  ──► backend/app/advisory/      ──► Bilingual NDMA Playbooks
7. Zero False Clinical Claims   ──► docs/LIMITATIONS.md        ──► Relative Risk (0-100)
```
