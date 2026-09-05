# Data Access Tier Classification & Provenance Matrix

This document maps all potential data streams for heatwave early warning against the Hermes Autonomous Operating Framework tiers.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            DATA SOURCE TIERS                                 │
│                                                                              │
│  [ Tier 1: Automated MVP ]                                                   │
│   ├── NASA POWER API (40y hourly reanalysis baseline)  ───► 200 OK Live      │
│   ├── Open-Meteo High-Res NWP (5-day forward forecast) ───► 200 OK Live      │
│   ├── Census of India 2011 PCA (Ward vulnerability)    ───► Public Baseline  │
│   ├── UTCI / ISO 7243 WBGT Scientific Formulations     ───► Pure Physics     │
│   └── NDMA / NCDC Heat Action Plan Advisory Framework  ───► Public Guidance  │
│                                                                              │
│  [ Tier 2: Requires Account / Manual Configuration ]                         │
│   ├── NCMRWF Raw High-Res Ensemble (NWP Portal)        ───► Form/Gov Reg     │
│   ├── MOSDAC INSAT-3D/3DR Satellite Land Surface Temp  ───► User Token Auth  │
│   └── Copernicus ERA5 CDS API                          ───► API Key / EULA   │
│                                                                              │
│  [ Tier 3: Requires Institutional / Human Clearance ]                        │
│   ├── NHRIDS / IDSP Daily Hospital Heatstroke Records  ───► Confidential     │
│   ├── Municipal Daily Cause-Specific Death Registers   ───► Non-Public       │
│   └── Real-time Smart Power-Grid Substation Telemetry  ───► Discom Internal  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Status Breakdown

### **Tier 1 — Fully Integrated Automated MVP (Zero Human Intervention)**
1. **NASA POWER API (LaRC):**
   - *Status:* Integrated.
   - *Method:* Keyless REST JSON query.
   - *Usage:* Historical climatological normals, percentile thresholds, rural spatial backfill.
2. **Open-Meteo Forecast Engine:**
   - *Status:* Integrated.
   - *Method:* Keyless REST JSON query.
   - *Usage:* Forward 3–5 day predictive forecast variables ($T2M, RH, WS, GHI$).
3. **Census of India Primary Census Abstract:**
   - *Status:* Ingested as clean local ward baseline.
   - *Usage:* Heat Vulnerability Index (HVI) demographic weights.
4. **UTCI & ISO 7243 Formulations:**
   - *Status:* Implemented in Python scientific modules (`utci_engine.py`, `wbgt_engine.py`).

---

### **Tier 2 — Requires Developer Account / API Token (Future Refinement Layer)**
1. **MOSDAC (ISRO INSAT-3D/3DR LST Data):**
   - *Why Hermes cannot auto-access:* Requires an approved user login at mosdac.gov.in and manual token generation per the Download API manual.
   - *Human Action Needed:* Register on MOSDAC portal, generate download token, configure `MOSDAC_TOKEN` in `.env`.
   - *Integration Path:* Pluggable satellite surface temperature layer refining micro-urban heat island offsets.
2. **NCMRWF Operational Ensemble GRIB2 Streams:**
   - *Why Hermes cannot auto-access:* Hosted on institutional research data systems with IP filtering or institutional credentials.
   - *Human Action Needed:* Request MoU / Academic research credentials from MoES/NCMRWF.
   - *Integration Path:* Drop-in replacement for Open-Meteo forward forecast adapter.

---

### **Tier 3 — Requires Institutional / Medical Clearance (Production Governance Layer)**
1. **NHRIDS / IDSP Hospital Emergency Admissions:**
   - *Why Hermes cannot auto-access:* Protected health information governed by patient privacy and Ministry of Health protocols.
   - *Human Action Needed:* Formal institutional research ethics clearance and health ministry data-sharing agreements.
   - *Integration Path:* Retrospective supervised training for clinical hospital bed surge prediction.
