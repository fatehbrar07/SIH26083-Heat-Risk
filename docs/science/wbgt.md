# Wet-Bulb Globe Temperature (WBGT) — ISO 7243 & NIOSH Occupational Methodology

## 1. Concept & Background
The **Wet-Bulb Globe Temperature (WBGT)** is the primary global standard for evaluating occupational heat stress and physical work-rest limits (ISO 7243:2017 and NIOSH Criteria 2016).

Unlike indoor dry-bulb temperature, outdoor WBGT models three fundamental physical heat exchange mechanisms:
1. **Natural Wet-Bulb Temperature ($T_{nw}$):** Represents evaporative cooling capacity under natural ambient ventilation and moisture.
2. **Black Globe Temperature ($T_g$):** Represents radiant heat absorption from direct sunlight and reflected ground radiation.
3. **Dry-Bulb Air Temperature ($T_a$):** Ambient convective temperature.

---

## 2. Standard Mathematical Formulation

For outdoor environments with direct solar load (the standard case for Indian outdoor laborers, construction workers, and agricultural workers):

$$\text{WBGT}_{outdoor} = 0.7\,T_{nw} + 0.2\,T_g + 0.1\,T_a$$

Where:
* $T_a$: Ambient 2m dry-bulb temperature (°C)
* $T_{nw}$: Natural wet-bulb temperature (°C), calculated via Stull's psychrometric formulation:
  $$T_{nw} \approx T_a \text{ atan}\left(0.151977 \sqrt{RH + 8.313659}\right) + \text{atan}(T_a + RH) - \text{atan}(RH - 1.676331) + 0.00391838 \sqrt{RH^3} \text{ atan}(0.023101 RH) - 4.686035$$
* $T_g$: Black globe temperature (°C), estimated from solar irradiance ($GHI$) and wind speed ($v$ in m/s) via ISO/Liljegren approximations:
  $$T_g \approx T_a + 0.0128 \times GHI - 0.52 \times \sqrt{\max(v, 0.5)}$$

---

## 3. NIOSH / ISO 7243 Work-Rest Interventions

| WBGT Range (°C) | Risk Level | Mandatory Occupational Intervention | Hourly Fluid Intake |
| :--- | :--- | :--- | :--- |
| $< 26.0^\circ\text{C}$ | **Normal** | Continuous normal work (100%). | 0.5 Liters / hour |
| $26.0 - 27.9^\circ\text{C}$ | **Caution** | 75% work / 25% rest per hour under shade. | 0.75 Liters / hour |
| $28.0 - 29.9^\circ\text{C}$ | **Warning** | 50% work / 50% rest per hour. Stagger heavy physical shifts. | 1.00 Liters / hour |
| $30.0 - 31.9^\circ\text{C}$ | **Danger** | 25% work / 75% rest per hour. Pre-position electrolyte hydration stations. | 1.00 Liters / hour |
| $\ge 32.0^\circ\text{C}$ | **Extreme Danger** | **Halt all unconditioned outdoor physical labor.** Critical risk of heat collapse. | $\ge 1.25$ Liters / hour |
