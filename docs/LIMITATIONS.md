# Scientific, Data & Operational Limitations

To ensure absolute engineering and scientific integrity, this document explicitly details the boundaries and limitations of the SIH26083 prototype.

---

## 1. Meteorological Resolution vs. Ward Spatial Attribution
* **Limitation:** Global meteorological models (Open-Meteo) and satellite reanalysis (NASA POWER) operate on continuous spatial grids (ranging from $1\text{ km}$ to $0.5^\circ \approx 50\text{ km}$).
* **Honest Clarification:** The system does **not** claim that the raw numerical weather prediction model computes separate convective physics for every single municipal street or ward.
* **Our Method:** Meteorological grids are spatially mapped and downscaled across ward polygons, where local variation is driven by the **Heat Vulnerability Index (HVI)** (demographics, urban density, and surface characteristics).

---

## 2. Mortality & Clinical Modeling Boundaries
* **Limitation:** Real-time daily cause-specific mortality counts at ward level are not publicly accessible in India.
* **Honest Clarification:** This prototype does **not** claim to predict "14 deaths tomorrow in Ward 3". Any system making such claims without verified daily training labels is unscientific.
* **Our Method:** We output a **Relative Human Heat-Health Risk Score (0–100)** calibrated on peer-reviewed epidemiological exposure-response curves (*Azhar et al. 2014, Mazdiyasni et al. 2017*) and retrospective historical hindcasts (Delhi June 2024).

---

## 3. Demographic Data Latency
* **Limitation:** The latest publicly released complete ward-level Primary Census Abstract in India is from Census 2011.
* **Honest Clarification:** Populations have expanded and urban boundaries have shifted since 2011.
* **Our Method:** Demographic shares (elderly %, informal housing %, outdoor labor %) are utilized as normalized relative vulnerability proxies rather than absolute census counts.

---

## 4. Reanalysis Latency in NASA POWER
* **Limitation:** NASA POWER MERRA-2 daily reanalysis data has an operational latency of 24–48 hours and cannot be used alone for forward forecasting.
* **Our Method:** NASA POWER provides the 40-year historical baseline for climatological normal and percentile calculation, while high-resolution Open-Meteo NWP feeds the forward 3–5 day early warning forecast.
