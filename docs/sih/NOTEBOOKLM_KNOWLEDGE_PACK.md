# SIH26083 — MASTER RESEARCH & PPT KNOWLEDGE PACK
## NotebookLM Source of Truth for Smart India Hackathon 2026 Presentation
*Compiled from the SIH26083 Research Artifacts, Biometeorological Science Baseline, and Production Prototype.*

---

## 1. PROJECT IDENTITY

- **Problem Statement ID:** `SIH26083`
- **Title:** Extreme Heatwave Early Warning and Human Thermal Stress Index
- **Organization:** Ministry of Earth Sciences (MoES)
- **Department:** National Centre for Medium Range Weather Forecasting (NCMRWF)
- **Category:** Software
- **Theme:** Disaster Management
- **Primary Official Source:** [https://sih.gov.in/sih2026PS](https://sih.gov.in/sih2026PS)
- **Secondary Problem-Statement Archive:** [https://github.com/vedantchalke36/sih-2026-problem-statements/blob/main/ps_2026/SIH26083.md](https://github.com/vedantchalke36/sih-2026-problem-statements/blob/main/ps_2026/SIH26083.md)
- **Solution Name:** **ThermoShield — AI-Driven Human Heat Risk & Early Warning System**
- **Subtitle:** *From Weather Forecasts → Human Thermal Stress → Localized Action*

---

## 2. OFFICIAL PROBLEM STATEMENT INTERPRETATION

Conventional heatwave early warning systems in India rely heavily on single-variable dry-bulb temperature ($T_{max}$) thresholds from regional IMD bulletins (e.g., $40^\circ\text{C}$ or $+4.5^\circ\text{C}$ departure from normal). However, the human body does not sense thermometer temperature alone — human survival depends on **thermoregulatory heat balance** governed by humidity (evaporative cooling), wind speed (convective cooling), and direct/diffuse solar irradiance.

The core mandate of SIH26083 is to transition heatwave warning systems:
> **"What the weather will do to humans"** rather than merely **"What the temperature will be."**

### The Core Conceptual Chain
$$\text{WEATHER FORECAST} \longrightarrow \text{THERMAL STRESS} \longrightarrow \text{HEALTH-IMPACT RISK} \longrightarrow \text{SPATIAL VULNERABILITY} \longrightarrow \text{TARGETED ACTION}$$

### Key Required Capabilities
1. **Multi-Variable Thermal Stress Index:** Combining temperature, humidity, wind velocity, and solar radiation.
2. **Standardized Indices (UTCI / WBGT / Heat Index):**
   - **UTCI (Universal Thermal Climate Index):** Broad outdoor human thermal strain based on the multi-node Fiala thermoregulatory model.
   - **WBGT (Wet-Bulb Globe Temperature, ISO 7243 / NIOSH):** Occupational threshold for outdoor laborers, gig workers, construction, and agriculture.
   - **Heat Index (NOAA NWS / Steadman):** Perceived temperature baseline.
3. **Localized 3–5 Day Anticipation:** Forecasting thermal stress 72h–120h in advance to enable proactive resource staging.
4. **Demographic Vulnerability (HVI):** Overlaying Census data (elderly population, children 0–6, outdoor/marginal workers, slum density, green canopy deficit).
5. **Ward/Zone GIS Risk Representation:** Clear spatial risk maps highlighting high-priority municipal sectors.
6. **Automated Action & Advisories:** Automated bilingual (English & Hindi) NDMA/NCDC health directives, DISCOM power surge readiness, and ISO 7243 work-rest cycles.

---

## 3. SCIENTIFIC FOUNDATION & FORMULATIONS

### 3.1 Universal Thermal Climate Index (UTCI)
- **Scientific Reference:** UTCI Consortium / WMO Commission for Climatology ([https://www.utci.org/](https://www.utci.org/)).
- **Formulation:** Evaluated via the 6th-order multi-variate polynomial approximation of the 187-node Fiala thermophysiological model:
  $$\text{UTCI} = f(T_a, T_{mrt} - T_a, v_{1.2}, e_a)$$
  Where $T_a$ is air temperature ($^\circ\text{C}$), $T_{mrt}$ is mean radiant temperature ($^\circ\text{C}$), $v_{1.2}$ is wind speed downscaled to human height ($1.2\text{ m}$), and $e_a$ is water vapor pressure ($\text{kPa}$).
- **Vapor Pressure Calculation (Buck, 1981):**
  $$e_s(T) = 0.61121 \cdot \exp\left(\left(18.678 - \frac{T}{234.84}\right) \cdot \frac{T}{257.14 + T}\right) \quad [\text{kPa}]$$
  $$e_a = e_s(T) \cdot \frac{RH}{100.0}$$
- **Logarithmic Wind Profile Downscaling:**
  $$v_{1.2} = v_{10} \cdot \frac{\log(1.2 / 0.01)}{\log(10.0 / 0.01)} \approx v_{10} \cdot 0.693$$
- **UTCI Stress Categories:**
  - $< +9^\circ\text{C}$: Slight to Extreme Cold Stress
  - $+9^\circ\text{C} \text{ to } +26^\circ\text{C}$: No Thermal Stress (Thermal Comfort)
  - $+26^\circ\text{C} \text{ to } +32^\circ\text{C}$: Moderate Heat Stress
  - $+32^\circ\text{C} \text{ to } +38^\circ\text{C}$: Strong Heat Stress
  - $+38^\circ\text{C} \text{ to } +46^\circ\text{C}$: Very Strong Heat Stress
  - $\ge +46^\circ\text{C}$: Extreme Heat Stress (Life-threatening physiological strain)

### 3.2 Wet-Bulb Globe Temperature (WBGT) — ISO 7243 / NIOSH Criteria
- **Reference:** NIOSH Occupational Exposure Criteria ([CDC/NIOSH Pub 2016-106](https://www.cdc.gov/niosh/docs/2016-106/pdfs/2016-106.pdf)).
- **Stull Psychrometric Natural Wet-Bulb ($T_w$):**
  $$T_w = T \cdot \arctan(0.151977 \cdot (RH + 8.313659)^{0.5}) + \arctan(T + RH) - \arctan(RH - 1.676331) + 0.00391838 \cdot (RH)^{1.5} \cdot \arctan(0.023101 \cdot RH) - 4.686035$$
- **Liljegren Outdoor Globe Radiation ($T_g$):**
  $$T_g \approx 0.0149 \cdot \text{SolarRadiation} + 1.009 \cdot T - 0.21 \cdot v_{10}^{0.5} + 0.6$$
- **Outdoor WBGT Formula:**
  $$\text{WBGT}_{\text{outdoor}} = 0.7\,T_w + 0.2\,T_g + 0.1\,T_a$$
- **ISO 7243 Work-Rest Schedules (Unacclimatized Heavy Labor):**
  - $\text{WBGT} < 26.0^\circ\text{C}$: Continuous work (100% Work / 0% Rest)
  - $26.0^\circ\text{C} \le \text{WBGT} < 29.0^\circ\text{C}$: 75% Work / 25% Rest (45 min work / 15 min rest)
  - $29.0^\circ\text{C} \le \text{WBGT} < 32.0^\circ\text{C}$: 50% Work / 50% Rest (30 min work / 30 min rest)
  - $\text{WBGT} \ge 32.0^\circ\text{C}$: 25% Work / 75% Rest or Suspend Unconditioned Manual Labor

### 3.3 Demographic Heat Vulnerability Index (HVI)
Constructed from Census 2011 Primary Census Abstract (PCA) indicators using min-max normalization:
$$\text{HVI}_i = 0.25 \cdot \tilde{X}_{\text{elderly}} + 0.15 \cdot \tilde{X}_{\text{child}} + 0.25 \cdot \tilde{X}_{\text{outdoor}} + 0.20 \cdot \tilde{X}_{\text{slum\_density}} + 0.15 \cdot (1 - \tilde{X}_{\text{green}})$$

### 3.4 Multi-Factor Composite Risk & Duration Penalty
Hazard ($H$) derived from UTCI, WBGT, and temperature departures is compounded by multi-day heat accumulation:
$$D_{\text{mult}} = 1.0 + 0.10 \cdot \min(\text{consecutive\_days} - 1, 4)$$
$$\text{Composite Risk Score} = \min(100.0, (0.65 \cdot H + 0.35 \cdot \text{HVI}) \cdot D_{\text{mult}})$$
- **NDMA Action Bands:**
  - `0–25`: Low (Green) — Normal awareness
  - `26–50`: Moderate (Yellow) — General hydration advisory
  - `51–75`: High (Orange) — Vulnerable population intervention, adjusted labor hours
  - `76–100`: Critical (Red) — Emergency cooling centers, water tankers, hospital surge activation

---

## 4. EPIDEMIOLOGICAL BENCHMARKS & 72h–120h ADVANCE LEAD-TIME

1. **Azhar et al. (2014) — PLoS ONE [PMID: 24632867]:**
   - Documented **1,344 excess all-cause deaths** (a **43.1% surge** above baseline) during the May 2010 Ahmedabad heatwave ($46.8^\circ\text{C}$ peak).
   - Proved that thermal mortality spikes non-linearly when sustained multi-day heat exceeds thermoregulatory limits.
2. **Mazdiyasni et al. (2017) — PNAS [PMID: 28584104]:**
   - Analysis of 50 years of IMD gridded records showed that a $+0.5^\circ\text{C}$ increase in mean summer temperature led to a **146% increase in the probability of mass-mortality heat events** ($>100$ deaths).
3. **Lead-Time Proof:**
   - Single-variable temperature warnings only trigger red alerts when temperatures breach extreme thresholds on D-Day or D-1.
   - ThermoShield integrates moisture and radiation with NWP 5-day forecasts, triggering **Orange/Red physiological stress alerts at D-5 (120h lead) and D-3 (72h lead)**, giving municipal authorities vital time to position cooling centers and hydrate workers.

---

## 5. EXACT 6-SLIDE PRESENTATION DECK STRUCTURE

### SLIDE 1 — TITLE PAGE
- **Heading:** SMART INDIA HACKATHON 2026
- **Problem Statement ID:** SIH26083
- **Problem Statement:** Extreme Heatwave Early Warning and Human Thermal Stress Index
- **Theme:** Disaster Management
- **PS Category:** Software
- **Team ID:** [TEAM ID] | **Team Name:** [TEAM NAME]
- **Solution Name:** **ThermoShield — AI-Driven Human Heat Risk & Early Warning System**
- **Subtitle:** *From Weather Forecasts → Human Thermal Stress → Localized Action*

### SLIDE 2 — IDEA TITLE & CORE INNOVATION
- **Core Narrative:** Temperature alone does not equal human risk. A dry 40°C allows sweat evaporation; a humid 40°C halts cooling, risking fatal hyperthermia.
- **Main Flowchart:**
  $$\text{WEATHER + SATELLITE + DEMOGRAPHICS} \longrightarrow \text{THERMAL ENGINE (UTCI/WBGT)} \longrightarrow \text{HEALTH-RISK MODEL} \longrightarrow \text{SPATIAL VULNERABILITY} \longrightarrow \text{AUTOMATED ACTION ENGINE}$$
- **4 Key Differentiators:**
  1. *Multidimensional Thermal Stress:* Evaluates temperature, humidity, wind, and radiation together.
  2. *Human-Impact Focus:* Translates atmospheric conditions into physiological strain.
  3. *Hyper-Local Vulnerability:* Ward/zone risk mapped via demographic vulnerability (elderly, laborers, slums).
  4. *Action Automation:* Automated bilingual (EN/HI) advisories, NIOSH work-rest schedules, and API triggers.
- **Bottom USP:** *"Not another heat map — an impact-to-action intelligence layer for heatwaves."*

### SLIDE 3 — TECHNICAL APPROACH & ARCHITECTURE
- **5-Layer Architecture:**
  1. *Data Ingestion:* Open-Meteo 5-day NWP, NASA POWER 30-year MERRA-2 climatology, Census 2011 PCA.
  2. *Data Processing:* Spatial alignment, wind profile downscaling ($10\text{m} \to 1.2\text{m}$), vapor pressure computation.
  3. *Thermal Stress Engine:* 6th-order UTCI polynomial + ISO 7243 Stull/Liljegren outdoor WBGT.
  4. *Risk Synthesis:* Hazard $\times$ HVI vulnerability with multi-day cumulative persistence penalty.
  5. *Decision & Delivery:* Leaflet GIS choropleth, Chart.js multi-day trends, Telegram Bot broadcaster, bilingual NDMA playbooks.
- **Compact Tech Stack:** Python 3.11, FastAPI, Pydantic v2, Leaflet.js, Chart.js, Docker.

### SLIDE 4 — FEASIBILITY & VIABILITY
- **Risk Mitigation Table:**
  - *Data Heterogeneity:* Harmonized into unified spatial grids and standardized JSON schemas.
  - *Temporal Baseline Gaps:* Solved using 30-year NASA POWER MERRA-2 historical climatology.
  - *Public Health Calibration:* Uses relative risk indices and established epidemiological literature rather than claiming unverified raw mortality numbers.
- **MVP to Scale Roadmap:**
  - *Phase 1:* Single-city prototype (Delhi NCR baseline).
  - *Phase 2:* Multi-city ward-level thermal & HVI mapping (Delhi, Ahmedabad, Surat, Bhubaneswar, Mumbai).
  - *Phase 3:* Predictive health-risk forecasting + automated Telegram dispatch.
  - *Phase 4:* Nationwide scaling with MoES / NCMRWF ensemble GRIB2 integration.

### SLIDE 5 — IMPACT & BENEFITS
- **72h–120h Timeline:**
  $$\text{D-5 (120h): Forecast Stress} \longrightarrow \text{D-3 (72h): High-Risk Ward Flag} \longrightarrow \text{D-2 (48h): Automated Alerts} \longrightarrow \text{D-1 (24h): Targeted Staging} \longrightarrow \text{D-Day: Reduced Mortality}$$
- **Target Beneficiaries:**
  - *Municipal Corporations:* Ward-level intervention and water tanker routing.
  - *Health Departments:* Emergency surge bed preparation and ORS stock prepositioning.
  - *Disaster Management (NDMA):* Pre-emptive Heat Action Plan activation.
  - *Citizens & Outdoor Workers:* NIOSH work-rest schedules and hydration alerts.
- **Triple Impact:**
  - *Social:* Protects outdoor laborers and vulnerable urban poor.
  - *Economic:* Reduces occupational heat illness and prevents uncoordinated grid shutdowns.
  - *Environmental:* Informs urban greening and cool-roof policy priorities.

### SLIDE 6 — RESEARCH & REFERENCES
- **1. Official / Government:** IMD Heatwave Guidance, NDMA Heat Action Plan guidelines, NCDC NPCCHH.
- **2. Thermal Stress Standards:** ISO 7243:2017 (WBGT), UTCI Consortium (Fiala multi-node model), NIOSH Heat Stress Criteria (2016).
- **3. Epidemiological Literature:** Azhar et al. (2014) *PLoS ONE* (Ahmedabad 2010 heatwave), Mazdiyasni et al. (2017) *PNAS* (Indian heatwave mortality scaling).
- **4. Open Data Provenance:** NASA POWER MERRA-2 API, Open-Meteo NWP, Census India 2011 Primary Census Abstract.
- **Highlighted Research Gap:** *"Existing meteorological systems provide weather forecasts, but lack integrated physiological thermal strain and ward-level demographic vulnerability to trigger pre-emptive public health action."*

---
*End of Master Knowledge Pack.*
