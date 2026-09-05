# NOAA / NWS Heat Index — Formulation & Limitations

## 1. Formulation
The **National Weather Service (NWS) Heat Index (HI)** is an empirical apparent temperature derived from Robert G. Steadman's 1979 biometeorological studies. It estimates how hot it feels when relative humidity is combined with air temperature.

The operational calculation utilizes the multi-parameter **Rothfusz Regression Equation**:

$$HI = c_1 + c_2 T + c_3 RH + c_4 T RH + c_5 T^2 + c_6 RH^2 + c_7 T^2 RH + c_8 T RH^2 + c_9 T^2 RH^2$$

*(Constants $c_1 \dots c_9$ are calibrated for $T$ in °F and converted to °C)*.

---

## 2. Fundamental Limitations for Indian Operations
While widely used in basic weather apps, the Heat Index has major limitations that make it unsuitable as a standalone operational metric for SIH26083:
1. **Zero Solar Radiation Factor:** Heat Index assumes full shade and indoor ventilation ($v \approx 2.5\text{ m/s}$). It completely ignores direct solar irradiance ($GHI$), which adds $5^\circ\text{C}$ to $12^\circ\text{C}$ of equivalent thermal stress in outdoor Indian environments.
2. **Static Wind Assumption:** Ignores varying wind speeds that dictate convective heat dissipation.
3. **Upper-Bound Mathematical Distortion:** At extreme combinations ($T > 42^\circ\text{C}$ with $RH > 60\%$), polynomial extrapolation produces asymptotic spikes ($HI > 75^\circ\text{C}$), losing precise physiological meaning.

*Conclusion:* Heat Index is retained in SIH26083 solely as a **comparison baseline**, while **UTCI** and **WBGT** serve as primary physiological engines.
