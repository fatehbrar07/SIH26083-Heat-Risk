# SIH Presentation & Pitch Narrative Guide

## SIH26083 — Extreme Heatwave Early Warning and Human Thermal Stress Index
**Ministry of Earth Sciences (MoES) / NCMRWF**

This document aligns the working prototype directly to the official 6-slide Smart India Hackathon format.

---

### Slide 1: Title & Team Information
- **Problem Statement ID:** `SIH26083`
- **Title:** Extreme Heatwave Early Warning and Human Thermal Stress Index
- **Department / Ministry:** National Centre for Medium Range Weather Forecasting (NCMRWF) / Ministry of Earth Sciences (MoES)
- **Category:** Software
- **Theme:** Disaster Management
- **Project Name:** `ThermoGuard AI — Operational Human Heat-Health Early Warning System`
- **Core Pitch Hook (10s):** *"Conventional weather systems forecast ambient temperature. ThermoGuard AI forecasts human physiological survivability 3 to 5 days in advance."*

---

### Slide 2: Idea & Proposed Solution
- **The Core Problem:** Air temperature alone ($T2M$) is fundamentally inadequate for public health protection. A dry $40^\circ\text{C}$ allows sweat evaporation; a humid $40^\circ\text{C}$ halts evaporative cooling, resulting in rapid core hyperthermia and fatal heatstroke.
- **Our Solution:** A biometeorological risk operating system that:
  1. Computes the **Universal Thermal Climate Index (UTCI)** and **ISO 7243 WBGT** by fusing temperature, humidity, wind, and solar radiation.
  2. Overlays hyper-local socio-demographic vulnerability (**Heat Vulnerability Index - HVI**) using Census data (elderly share, outdoor workers, slum density).
  3. Projects a **3–5 day predictive risk window** to trigger pre-emptive municipal and hospital interventions before casualties occur.

---

### Slide 3: Technical Approach & Architecture
- **Data Ingestion (Tier-1 Public APIs):**
  - *NASA POWER API (LaRC):* 40-year daily climatological baseline (MERRA-2 reanalysis) for anomaly baselines.
  - *Open-Meteo High-Resolution NWP:* 5-day hourly forecast ($T2M, RH, WS, GHI$) at $0.1^\circ$ resolution.
- **Scientific Computing Core:**
  - *UTCI Engine:* Multi-node Fiala human thermoregulatory polynomial formulation.
  - *WBGT Engine:* Natural wet-bulb and black-globe calculation for NIOSH occupational safety limits.
- **Spatial & Risk Engine:**
  - Fast GIS spatial attribution mapping gridded weather to municipal ward polygons without claiming fake micro-sensor weather.
  - Non-linear multi-day duration compounding ($1.10\times$ to $1.30\times$).
- **API & Dispatch:**
  - High-performance FastAPI backend serving interactive Leaflet.js dashboards and bilingual (English & Hindi) municipal playbooks.

---

### Slide 4: Feasibility, Viability & Operational Reality
- **100% Operational Today:** Powered entirely by keyless, verified open-access REST APIs with zero recurring licensing cost.
- **Modular Scalability:** Can be deployed to any Indian municipality or state disaster authority (SDMA) by simply importing local ward GeoJSON boundaries and Census demographic parameters.
- **Honest Limitations & Defensibility:**
  - Avoids fabricated mortality predictions by presenting normalized **Relative Heat-Health Risk (0–100)**.
  - Solves the rural weather station sparsity problem via satellite-derived reanalysis backfills.
  - Applies a multi-hour persistence filter to prevent false alarms from disrupting outdoor labor productivity.

---

### Slide 5: Impact & Public Health Benefits
- **Municipal Preparedness:** Equips municipal commissioners with 72h–120h lead time to open emergency cooling centers, deploy water tankers to informal settlements, and alert power distribution companies.
- **Occupational Worker Protection:** Implements actionable NIOSH work-rest schedules (e.g., 50% rest under shade when outdoor WBGT $\ge 30^\circ\text{C}$) to protect construction and gig workers.
- **Healthcare Surge Readiness:** Enables emergency departments to pre-position IV fluids, ice packs, and ORS corners in outpatient departments prior to peak heat stress hours.

---

### Slide 6: Research Grounding & Scientific References
1. **ISO 7243:2017** — *Ergonomics of the thermal environment — Assessment of heat stress using the WBGT index.*
2. **Bröde et al. (2012)** — *Deriving the operational procedure for the Universal Thermal Climate Index (UTCI).*
3. **National Disaster Management Authority (NDMA 2024)** — *National Guidelines for Preparation of Action Plan - Prevention and Management of Heat Wave.*
4. **Azhar et al. (2014) PLoS ONE** — *Heat-Related Mortality in India: Excess All-Cause Mortality Associated with the 2010 Ahmedabad Heat Wave.*
5. **Mazdiyasni et al. (2017) PNAS** — *Increasing probability of mortality during Indian heat waves.*
6. **NASA POWER Project (NASA LaRC)** — *Prediction Of Worldwide Energy Resources daily meteorological reanalysis.*
