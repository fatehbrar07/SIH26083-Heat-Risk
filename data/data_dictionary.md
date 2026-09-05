# Data Dictionary — SIH26083 Human Thermal Risk Engine

| Variable Name | Source | Native Units | Transformation / Scale | Meaning & Physiological Significance | Used By Module |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `T2M` / `temperature_2m` | NASA POWER / Open-Meteo | °C | None | Dry-bulb air temperature at 2 meters above ground. Standard meteorological metric. | Thermal Engine, UTCI, WBGT, HI |
| `RH2M` / `relative_humidity_2m`| NASA POWER / Open-Meteo | % (0–100) | Converted to water vapor pressure ($e$) in kPa | Relative humidity at 2 meters. Directly governs sweat evaporation rate and latent cooling capacity. | Thermal Engine, UTCI, WBGT, HI |
| `WS2M` / `wind_speed_2m` | NASA POWER / Open-Meteo | m/s | Clamped to physiological limits ($0.5 \le v \le 17\text{ m/s}$) | 2-meter horizontal wind speed. Determines convective heat transfer and boundary layer resistance. | Thermal Engine, UTCI, WBGT |
| `ALLSKY_SFC_SW_DWN` / `GHI` | NASA POWER / Open-Meteo | $\text{W/m}^2$ or $\text{MJ/m}^2/\text{day}$ | Converted to $\text{W/m}^2$ and Mean Radiant Temperature ($T_{mrt}$) | All-sky surface shortwave downward irradiance (Global Horizontal Irradiance). Determines direct radiative heat load on human body. | Thermal Engine, UTCI, WBGT |
| `UTCI` | Computed (ECMWF / WMO model) | °C | 10-level categorical stress scale | Universal Thermal Climate Index. Equivalent temperature assessing dynamic human multi-node thermoregulation. | Thermal Engine, Hazard Scoring |
| `WBGT` | Computed (ISO 7243) | °C | Simplified Outdoor / Liljegren formulation | Wet-Bulb Globe Temperature ($0.7 T_w + 0.2 T_g + 0.1 T_a$). Standard for occupational work-rest cycles. | Advisory Engine, Occupational Risk |
| `Heat_Index` | Computed (NOAA NWS) | °C | Rothfusz regression equation | Apparent temperature based on Steadman's human model of biometeorology. | Comparison & Baseline Engine |
| `elderly_share` | Census of India (2011 PCA) | Fraction (0.0–1.0) | Min-Max normalized (0–100) | Proportion of ward population aged 60+ (higher cardiovascular strain and impaired sweating). | Vulnerability Engine (HVI) |
| `children_share` | Census of India (2011 PCA) | Fraction (0.0–1.0) | Min-Max normalized (0–100) | Proportion of ward population aged 0–6 (underdeveloped thermoregulation, high surface-area-to-mass ratio). | Vulnerability Engine (HVI) |
| `outdoor_worker_share` | Census 2011 & NSSO Labor Proxy | Fraction (0.0–1.0) | Min-Max normalized (0–100) | Proportion of workers in construction, informal gig-work, and street vending without thermal conditioning. | Vulnerability Engine (HVI) |
| `population_density` | Census 2011 & Municipal bounds | Persons / $\text{km}^2$ | Min-Max normalized (0–100) | Crowding proxy amplifying micro-urban heat island (UHI) effects and reducing nocturnal cooling. | Vulnerability Engine (HVI) |
| `informal_housing_share` | Census 2011 Housing / Slum | Fraction (0.0–1.0) | Min-Max normalized (0–100) | Percentage of households with tin/asbestos roofing, lacking adequate thermal insulation and ventilation. | Vulnerability Engine (HVI) |
| `HVI` | Computed | Score (0–100) | Categorical (Low to Extreme) | Heat Vulnerability Index: weighted demographic and socio-spatial susceptibility score. | Risk Matrix Engine |
| `Hazard_Score` | Computed | Score (0–100) | Continuous mapping from UTCI/WBGT | Physical thermal exposure score normalized to 0–100. | Risk Matrix Engine |
| `Human_Heat_Risk` | Computed | Score (0–100) | 4-Tier Bands (Low, Moderate, High, Very High) | Composite risk score ($0.60 \times \text{Hazard} + 0.40 \times \text{HVI}$) multiplied by duration persistence. | GIS Layer, Alert & Advisory Engine |
