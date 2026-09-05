import math
from typing import Dict, Any, Optional

class WBGTEngine:
    """
    Scientific implementation of the Wet-Bulb Globe Temperature (WBGT)
    grounded in ISO 7243:2017 and NIOSH criteria (2016).
    Models thermodynamic equilibrium across natural wet-bulb psychrometry,
    black-globe solar-convection heat balance, and ambient dry-bulb temperature.
    """

    ISO_7243_THRESHOLDS = {
        "light": {"acclimatized": 30.0, "unacclimatized": 27.5},
        "moderate": {"acclimatized": 28.0, "unacclimatized": 25.0},
        "heavy": {"acclimatized": 26.0, "unacclimatized": 22.5},
        "very_heavy": {"acclimatized": 25.0, "unacclimatized": 20.0}
    }

    @staticmethod
    def calculate_natural_wet_bulb_stull(
        temp_c: float,
        rh_pct: float,
        solar_radiation_w_m2: float = 0.0,
        wind_speed_ms: float = 1.0
    ) -> float:
        """
        Calculate natural wet-bulb temperature (T_nw, in °C) using Stull's (2011) psychrometric equation
        coupled with solar wick radiative absorption and convective dissipation per ISO 7243:2017.
        """
        t = temp_c
        rh = max(1.0, min(100.0, rh_pct))

        # Aspirated / Psychrometric wet-bulb baseline (Stull 2011)
        tw_aspirated = (
            t * math.atan(0.151977 * math.sqrt(rh + 8.313659))
            + math.atan(t + rh)
            - math.atan(rh - 1.676331)
            + 0.00391838 * (rh ** 1.5) * math.atan(0.023101 * rh)
            - 4.686035
        )
        # Wet bulb can never exceed dry-bulb air temperature under equilibrium
        tw_aspirated = min(t, tw_aspirated)

        ghi = max(0.0, solar_radiation_w_m2)
        v = max(0.1, wind_speed_ms)

        # Natural wet bulb wick solar radiative gain delta (Bernard & Pourmoghani / ISO 7243)
        delta_rad = (0.0015 * ghi) / (math.sqrt(v) + 0.3) if ghi > 0.0 else 0.0
        t_nw = tw_aspirated + delta_rad
        return round(t_nw, 2)

    @classmethod
    def calculate_natural_wet_bulb(
        cls,
        temp_c: float,
        rh_pct: float,
        wind_speed_ms: float = 1.0,
        solar_radiation_w_m2: float = 0.0
    ) -> float:
        """Alias for calculate_natural_wet_bulb_stull."""
        return cls.calculate_natural_wet_bulb_stull(
            temp_c=temp_c,
            rh_pct=rh_pct,
            solar_radiation_w_m2=solar_radiation_w_m2,
            wind_speed_ms=wind_speed_ms
        )

    @staticmethod
    def calculate_black_globe_temp(
        temp_c: float,
        wind_speed_ms: float,
        solar_radiation_w_m2: float,
        globe_diameter_m: float = 0.15,
        globe_emissivity: float = 0.95,
        globe_absorptivity: float = 0.95
    ) -> float:
        """
        Calculate equilibrium temperature of standard 150mm matte-black copper sphere (Tg, in °C).
        Models coupled Stefan-Boltzmann radiative exchange and forced convective dissipation (Liljegren et al. / ISO 7243:2017).
        """
        ghi = max(0.0, solar_radiation_w_m2)
        if ghi <= 0.0:
            return round(temp_c, 2)

        v = max(0.1, wind_speed_ms)
        sigma = 5.670374419e-8
        t_a_k = temp_c + 273.15

        # Convective heat transfer coefficient for sphere (h_c in W/m^2*K)
        # Nu = 2.0 + 0.6 * Re^0.5 * Pr^0.33
        # Standard Liljegren approximation: h_c = 1.4 * (v / D)^0.6 * k_air
        h_c = max(5.0, 6.3 * (v ** 0.6) / (globe_diameter_m ** 0.4))

        # Radiative heat flux absorbed per unit surface area of sphere
        s_rad = globe_absorptivity * (ghi / 2.0)

        # Solve nonlinear Stefan-Boltzmann + convective balance via Newton-Raphson:
        # epsilon * sigma * (Tg^4 - Ta^4) + h_c * (Tg - Ta) - S_rad = 0
        tg_k = t_a_k + (s_rad / (h_c + 4.0 * globe_emissivity * sigma * (t_a_k ** 3)))
        for _ in range(15):
            f = globe_emissivity * sigma * (tg_k ** 4 - t_a_k ** 4) + h_c * (tg_k - t_a_k) - s_rad
            df = 4.0 * globe_emissivity * sigma * (tg_k ** 3) + h_c
            step = f / df
            tg_k -= step
            if abs(step) < 1e-4:
                break

        tg = tg_k - 273.15
        return round(tg, 2)

    @classmethod
    def calculate_black_globe_temperature(
        cls,
        temp_c: float,
        rh_pct: float = 50.0,
        wind_speed_ms: float = 1.0,
        solar_radiation_w_m2: float = 0.0,
        globe_diameter_m: float = 0.15
    ) -> float:
        """Alias for calculate_black_globe_temp."""
        return cls.calculate_black_globe_temp(
            temp_c=temp_c,
            wind_speed_ms=wind_speed_ms,
            solar_radiation_w_m2=solar_radiation_w_m2,
            globe_diameter_m=globe_diameter_m
        )

    @classmethod
    def calculate_outdoor_wbgt(
        cls,
        temp_c: float,
        rh_pct: float,
        wind_speed_2m_ms: float,
        solar_radiation_w_m2: float = 0.0
    ) -> float:
        """
        Calculate standard Outdoor WBGT (°C) per ISO 7243:2017:
        WBGT = 0.7 * T_nw + 0.2 * T_g + 0.1 * T_a
        """
        t_nw = cls.calculate_natural_wet_bulb_stull(temp_c, rh_pct, solar_radiation_w_m2, wind_speed_2m_ms)
        t_g = cls.calculate_black_globe_temp(temp_c, wind_speed_2m_ms, solar_radiation_w_m2)
        t_a = temp_c

        wbgt = (0.7 * t_nw) + (0.2 * t_g) + (0.1 * t_a)
        return round(wbgt, 2)

    @classmethod
    def calculate_indoor_wbgt(
        cls,
        temp_c: float,
        rh_pct: float
    ) -> float:
        """
        Calculate standard Indoor / Shaded WBGT (°C) per ISO 7243:2017:
        WBGT = 0.7 * T_nw + 0.3 * T_g (where T_g ≈ T_a in the absence of direct solar irradiance)
        """
        t_nw = cls.calculate_natural_wet_bulb_stull(temp_c, rh_pct, 0.0, 1.0)
        t_g = temp_c
        wbgt = (0.7 * t_nw) + (0.3 * t_g)
        return round(wbgt, 2)

    @classmethod
    def calculate_wbgt_assessment(
        cls,
        temp_c: float,
        rh_pct: float,
        wind_speed_ms: float = 1.5,
        solar_radiation_w_m2: float = 0.0,
        is_outdoor: bool = True
    ) -> Dict[str, Any]:
        """
        Compute complete ISO 7243:2017 WBGT metrics and diagnostic components.
        """
        t_nw = cls.calculate_natural_wet_bulb_stull(temp_c, rh_pct, solar_radiation_w_m2 if is_outdoor else 0.0, wind_speed_ms)
        t_g = cls.calculate_black_globe_temp(temp_c, wind_speed_ms, solar_radiation_w_m2 if is_outdoor else 0.0)
        
        if is_outdoor:
            wbgt_val = (0.7 * t_nw) + (0.2 * t_g) + (0.1 * temp_c)
        else:
            wbgt_val = (0.7 * t_nw) + (0.3 * t_g)
        
        wbgt_val = round(wbgt_val, 1)
        adv = cls.get_occupational_advisory(wbgt_val)

        return {
            "wbgt_c": wbgt_val,
            "is_outdoor": is_outdoor,
            "dry_bulb_temp_c": temp_c,
            "natural_wet_bulb_c": t_nw,
            "globe_temp_c": t_g,
            "relative_humidity_pct": rh_pct,
            "wind_speed_ms": wind_speed_ms,
            "solar_radiation_w_m2": solar_radiation_w_m2 if is_outdoor else 0.0,
            "flag_condition": adv["flag_condition"],
            "risk_band": adv["risk_band"],
            "work_rest_ratio": adv["work_rest_ratio"],
            "water_intake_liters_per_hour": adv["water_intake_liters_per_hour"],
            "occupational_guideline": adv["occupational_guideline"]
        }

    @classmethod
    def get_work_rest_recommendation(
        cls,
        wbgt_c: float,
        workload_category: str = "moderate",
        acclimatized: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate ISO 7243:2017 / NIOSH recommended work-rest cycles based on workload and acclimatization.
        """
        norm_cat = workload_category.lower().replace(" ", "_")
        if norm_cat not in cls.ISO_7243_THRESHOLDS:
            norm_cat = "moderate"

        thresh_dict = cls.ISO_7243_THRESHOLDS[norm_cat]
        base_thresh = thresh_dict["acclimatized"] if acclimatized else thresh_dict["unacclimatized"]

        excess = wbgt_c - base_thresh

        if excess <= 0.0:
            return {
                "work_percentage": 100,
                "rest_percentage": 0,
                "cycle_label": "Continuous Work (100% Work / 0% Rest)",
                "work_stoppage_mandated": False,
                "recommended_water_l_hr": 0.5,
                "threshold_wbgt_c": base_thresh,
                "excess_wbgt_c": round(excess, 1)
            }
        elif excess <= 1.5:
            return {
                "work_percentage": 75,
                "rest_percentage": 25,
                "cycle_label": "75% Work / 25% Rest (45 min work / 15 min rest per hour)",
                "work_stoppage_mandated": False,
                "recommended_water_l_hr": 0.75,
                "threshold_wbgt_c": base_thresh,
                "excess_wbgt_c": round(excess, 1)
            }
        elif excess <= 3.0:
            return {
                "work_percentage": 50,
                "rest_percentage": 50,
                "cycle_label": "50% Work / 50% Rest (30 min work / 30 min rest per hour)",
                "work_stoppage_mandated": False,
                "recommended_water_l_hr": 1.0,
                "threshold_wbgt_c": base_thresh,
                "excess_wbgt_c": round(excess, 1)
            }
        elif excess <= 4.5:
            return {
                "work_percentage": 25,
                "rest_percentage": 75,
                "cycle_label": "25% Work / 75% Rest (15 min work / 45 min rest per hour)",
                "work_stoppage_mandated": False,
                "recommended_water_l_hr": 1.25,
                "threshold_wbgt_c": base_thresh,
                "excess_wbgt_c": round(excess, 1)
            }
        else:
            return {
                "work_percentage": 0,
                "rest_percentage": 100,
                "cycle_label": "Mandatory Work Stoppage (Halt strenuous physical activity)",
                "work_stoppage_mandated": True,
                "recommended_water_l_hr": 1.5,
                "threshold_wbgt_c": base_thresh,
                "excess_wbgt_c": round(excess, 1)
            }

    @staticmethod
    def get_occupational_advisory(wbgt_val: float) -> Dict[str, Any]:
        """
        Standard ISO 7243:2017 / ACGIH / US Army WBGT occupational and athletic flags.
        """
        if wbgt_val >= 32.2:
            return {
                "flag_condition": "Black Flag",
                "risk_band": "Extreme Hazard",
                "category": "Extreme Hazard",
                "color": "#000000",
                "work_rest_ratio": "15 min work / 45 min rest per hour (or cease strenuous outdoor labor)",
                "water_intake_liters_per_hour": 1.0,
                "occupational_guideline": "Mandatory halt of heavy outdoor manual labor. Extreme danger of exertional heat stroke."
            }
        elif wbgt_val >= 31.1:
            return {
                "flag_condition": "Red Flag",
                "risk_band": "Severe Hazard",
                "category": "Severe Hazard",
                "color": "#FF0000",
                "work_rest_ratio": "20 min work / 40 min rest per hour",
                "water_intake_liters_per_hour": 1.0,
                "occupational_guideline": "Strenuous exercise curtailed for all outdoor workers; continuous shaded breaks mandatory."
            }
        elif wbgt_val >= 29.4:
            return {
                "flag_condition": "Yellow Flag",
                "risk_band": "High Hazard",
                "category": "High Hazard",
                "color": "#EAB308",
                "work_rest_ratio": "30 min work / 30 min rest per hour",
                "water_intake_liters_per_hour": 0.75,
                "occupational_guideline": "Unacclimatized workers must avoid strenuous outdoor activity; mandatory hydration checkpoints."
            }
        elif wbgt_val >= 26.7:
            return {
                "flag_condition": "Green Flag",
                "risk_band": "Moderate Hazard",
                "category": "Moderate Hazard",
                "color": "#22C55E",
                "work_rest_ratio": "45 min work / 15 min rest per hour",
                "water_intake_liters_per_hour": 0.5,
                "occupational_guideline": "Heavy physical exertion should be performed with caution and continuous fluid replenishment."
            }
        else:
            return {
                "flag_condition": "White / Normal Flag",
                "risk_band": "Low Hazard",
                "category": "Low Hazard",
                "color": "#3B82F6",
                "work_rest_ratio": "Continuous work permitted (with standard breaks)",
                "water_intake_liters_per_hour": 0.5,
                "occupational_guideline": "Normal activities permitted. Maintain standard workplace hydration."
            }
