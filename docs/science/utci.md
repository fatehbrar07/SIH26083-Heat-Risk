# Universal Thermal Climate Index (UTCI) — Scientific Methodology & Implementation

## 1. Concept & Theoretical Grounding
The **Universal Thermal Climate Index (UTCI)** is the international scientific gold-standard biometeorological metric (developed by the UTCI Commission and WMO). Unlike empirical indices like Heat Index or Wind Chill, UTCI is derived from the **Fiala Multi-Node Human Physiology and Thermal Comfort Model**.

The Fiala model treats the human body as 12 spherical or cylindrical body segments subdivided into 187 tissue layers, coupled with an active thermoregulatory system simulating:
* Vasodilation and vasoconstriction
* Sweat secretion and latent evaporative cooling
* Shivering and metabolic heat production

The UTCI equivalent temperature ($UTCI$, in °C) is defined as the air temperature ($T_a$) of a reference environment (with $RH = 50\%$, $v_{10m} = 0.5\text{ m/s}$, and $T_{mrt} = T_a$) that produces the same dynamic physiological strain on the human body as the actual environment.

---

## 2. Mathematical Approximation & Input Variables

The full Fiala numerical simulation is computationally intensive. The UTCI scientific commission parameterized the model into a high-order polynomial response surface:

$$UTCI = f(T_a, T_{mrt}, v_{10m}, e)$$

Where:
* $T_a$: Air temperature at 2m (°C), valid range: $-50^\circ\text{C} \le T_a \le +50^\circ\text{C}$
* $T_{mrt}$: Mean Radiant Temperature (°C), computed from solar irradiance:
  $$T_{mrt} \approx T_a + \frac{0.7 \times GHI}{\sigma \cdot \epsilon} \cdot \left(\frac{1}{h_{c}}\right)$$
  (Simplified standard approximation: $T_{mrt} \approx T_a + 0.025 \times GHI$)
* $v_{10m}$: Wind speed at 10m height (m/s), related to 2m wind speed via logarithmic wind profile ($v_{10m} \approx v_{2m} \times 1.43$)
* $e$: Water vapor pressure (kPa), derived from Relative Humidity ($RH$) and saturation vapor pressure via the Magnus-Tetens formula:
  $$e_{sat}(T_a) = 0.61078 \exp\left(\frac{17.27 \times T_a}{T_a + 237.3}\right)\quad (\text{kPa})$$
  $$e = e_{sat}(T_a) \times \frac{RH}{100}$$

---

## 3. UTCI Thermal Stress Classification Scale

| UTCI Range (°C) | Stress Category | Physiological & Health Impact |
| :--- | :--- | :--- |
| $> +46.0$ | **Extreme Heat Stress** | Total failure of evaporative cooling; core temperature spikes rapidly toward lethal heatstroke ($>40.5^\circ\text{C}$). Life-threatening. |
| $+38.0 \text{ to } +46.0$ | **Very Strong Heat Stress** | Severe cardiovascular strain, profuse sweating leading to rapid dehydration, heavy strain on outdoor physical activity. |
| $+32.0 \text{ to } +38.0$ | **Strong Heat Stress** | Moderate to high physiological strain; thermoregulation maintained only with elevated heart rate and sweating. |
| $+26.0 \text{ to } +32.0$ | **Moderate Heat Stress** | Minor discomfort for general public; caution advised for elderly and unconditioned laborers. |
| $+9.0 \text{ to } +26.0$ | **No Thermal Stress** | Thermal neutrality / optimal comfort zone. |
| $< +9.0$ | **Cold Stress Tiers** | Slight to Extreme cold stress bands. |

---

## 4. Verification & Unit Validation
In this repository, the UTCI calculation is implemented in `backend/app/thermal/utci_engine.py` using standard polynomial regression verified against WMO reference test vectors.
