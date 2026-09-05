# Tier-1 Source Registry & Audit Provenance

This document catalogs every data source, scientific standard, and external endpoint utilized by the SIH26083 prototype. Every Tier-1 source listed is programmatically accessible without manual government approval, private API keys, or authenticated credentials.

---

## 1. Meteorological & Radiative Ingestion Sources

### 1.1 NASA POWER (Prediction Of Worldwide Energy Resources)
* **Organization:** NASA Langley Research Center (LaRC)
* **Portal / Documentation:** https://power.larc.nasa.gov/api/pages/ | https://power.larc.nasa.gov/parameters/
* **Endpoint:** `https://power.larc.nasa.gov/api/temporal/daily/point`
* **Access Tier:** **Tier 1 (Public REST, Zero Key Required, No Auth)**
* **Variables Extracted:**
  * `T2M`: Temperature at 2 Meters (°C)
  * `RH2M`: Relative Humidity at 2 Meters (%)
  * `WS2M`: Wind Speed at 2 Meters (m/s)
  * `ALLSKY_SFC_SW_DWN`: All Sky Surface Shortwave Downward Irradiance ($\text{MJ/m}^2/\text{day}$ or $\text{W/m}^2$)
* **Spatial & Temporal Resolution:** Global $0.5^\circ \times 0.625^\circ$ spatial grid, daily & hourly temporal coverage (1981–present).
* **Operational Role:** Provides 40-year climatological baseline normals, 95th percentile heatwave thresholds, and rural spatial backfill.

### 1.2 Open-Meteo High-Resolution NWP API
* **Organization:** Open-Meteo GmbH
* **Portal / Documentation:** https://open-meteo.com/en/docs
* **Endpoint:** `https://api.open-meteo.com/v1/forecast`
* **Access Tier:** **Tier 1 (Public REST, Keyless, Verified 200 OK)**
* **Variables Extracted:**
  * `temperature_2m`: Hourly air temperature (°C)
  * `relative_humidity_2m`: Hourly relative humidity (%)
  * `wind_speed_10m` / `wind_speed_2m`: Wind speed (converted to 2m equivalent)
  * `direct_radiation` & `diffuse_radiation`: Global Horizontal Irradiance ($\text{W/m}^2$)
* **Spatial & Temporal Resolution:** 1 km – 11 km grid based on ECMWF IFS, GFS, and DWD ICON ensembles; 1-to-5 day forward hourly forecast.
* **Operational Role:** Provides forward-looking 3–5 day predictive meteorological inputs to power early warning alerts.

---

## 2. Demographic & Vulnerability Baseline

### 2.1 Census of India (2011 Primary Census Abstract - PCA)
* **Organization:** Office of the Registrar General & Census Commissioner, India
* **Portal:** https://censusindia.gov.in/census.website/en/data/population_finder
* **Access Tier:** **Tier 1 (Public Open Data Archive)**
* **Indicators Extracted:** Ward-level Total Population, Age 60+ (Elderly share), Age 0–6 (Child share), Main & Marginal Manual Workers (Outdoor labor proxy), Housing materials (Slum/tin-roof proxy).
* **Explicit Limitation Note:** Coded strictly as **Census 2011 Baseline**. It provides relative spatial vulnerability distributions rather than 2026 exact real-time population counts.

---

## 3. Physiological Science & Health Guidance Standards

### 3.1 Universal Thermal Climate Index (UTCI)
* **Organization:** International Society of Biometeorology (ISB) & WMO Commission for Climatology
* **Methodology Document:** https://www.utci.org/resources/develop_utci.pdf | Błażejczyk et al. (2013)
* **Formula / Model:** Multi-node human thermoregulation model (Fiala et al.) parameterized into a 6th-degree polynomial approximation.
* **Access Tier:** **Tier 1 (Open Scientific Standard)**

### 3.2 ISO 7243:2017 & NIOSH Occupational Heat Stress
* **Organization:** International Organization for Standardization (ISO) & NIOSH/CDC
* **Documentation:** https://www.cdc.gov/niosh/heat-stress/recommendations/ | https://www.cdc.gov/niosh/docs/2016-106/pdfs/2016-106.pdf
* **Formula:** Outdoor Wet-Bulb Globe Temperature: $\text{WBGT} = 0.7 T_{nw} + 0.2 T_g + 0.1 T_a$.
* **Access Tier:** **Tier 1 (Open Occupational Standard)**

### 3.3 National Disaster Management Authority (NDMA) & NCDC
* **Organization:** NDMA India & National Centre for Disease Control (MoHFW)
* **Documentation:**
  * National Guidelines for Preparation of Action Plan - Heat Wave (2024): https://www.ndma.gov.in/
  * NCDC National Action Plan for Heat-Related Illnesses: https://ncdc.mohfw.gov.in/uploads/pdf/heat12.pdf
  * Report of Heat-Related Activities (2024 NPCCHH): https://www.ncdc.mohfw.gov.in/wp-content/uploads/2024/12/Report-of-Heat-Related-Activities-2024_NPCCHH.pdf
* **Access Tier:** **Tier 1 (Public Government Guidelines & Reports)**
