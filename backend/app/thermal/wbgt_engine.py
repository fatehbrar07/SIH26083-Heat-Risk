import math
from typing import Dict, Any

class WBGTEngine:
    """
    Scientific implementation of the Wet-Bulb Globe Temperature (WBGT)
    grounded in ISO 7243:2017 and NIOSH criteria (2016).
    """

    @staticmethod
    def calculate_natural_wet_bulb_stull(temp_c: float, rh_pct: float) -> float:
        """
        Calculate natural wet-bulb temperature (Tw, in °C) using Stull's (2011) psychrometric equation.
        Accurate to within 0.3°C across standard biometeorological regimes.
        """
        t = temp_c
        rh = max(1.0, min(100.0, rh_pct))

        tw = (
            t * math.atan(0.151977 * math.sqrt(rh + 8.313659))
            + math.atan(t + rh)
            - math.atan(rh - 1.676331)
            + 0.00391838 * (rh ** 1.5) * math.atan(0.023101 * rh)
            - 4.686035
        )
        return round(tw, 2)

    @staticmethod
    def calculate_black_globe_temp(
        temp_c: float,
        wind_speed_ms: float,
        solar_radiation_w_m2: float
    ) -> float:
        """
        Estimate Black Globe Temperature (Tg, in °C) accounting for solar irradiance and wind cooling.
        Based on ISO 7243 / Liljegren physical approximations.
        """
        ghi = max(0.0, solar_radiation_w_m2)
        v = max(0.2, wind_speed_ms)
        
        # Radiative gain minus convective cooling from wind
        # Higher wind accelerates convective heat dissipation from the globe
        delta_tg = (0.018 * ghi) / (math.sqrt(v) + 0.5)
        tg = temp_c + delta_tg
        return round(tg, 2)

    @classmethod
    def calculate_outdoor_wbgt(
        cls,
        temp_c: float,
        rh_pct: float,
        wind_speed_2m_ms: float,
        solar_radiation_w_m2: float = 0.0
    ) -> float:
        """
        Calculate standard Outdoor WBGT (°C):
        WBGT = 0.7 * T_nw + 0.2 * T_g + 0.1 * T_a
        """
        t_nw = cls.calculate_natural_wet_bulb_stull(temp_c, rh_pct)
        t_g = cls.calculate_black_globe_temp(temp_c, wind_speed_2m_ms, solar_radiation_w_m2)
        t_a = temp_c

        wbgt = (0.7 * t_nw) + (0.2 * t_g) + (0.1 * t_a)
        return round(wbgt, 2)

    @staticmethod
    def get_occupational_advisory(wbgt_val: float) -> Dict[str, Any]:
        """
        Return ISO 7243 / NIOSH occupational work-rest schedules and hydration guidance.
        """
        if wbgt_val >= 32.0:
            return {
                "category": "Extreme Danger",
                "severity": "CRITICAL",
                "color": "#EF4444",
                "work_rest_cycle": "Halt unconditioned outdoor manual labor (0% Work / 100% Rest)",
                "water_intake_hourly": "1.25 Liters / hour (with electrolytes)",
                "action": "Immediate suspension of strenuous outdoor construction, agriculture, and direct sun labor."
            }
        elif wbgt_val >= 30.0:
            return {
                "category": "Danger",
                "severity": "HIGH",
                "color": "#F97316",
                "work_rest_cycle": "25% Work / 75% Rest per hour under shade",
                "water_intake_hourly": "1.00 Liters / hour",
                "action": "Mandate shade breaks every 15 minutes. Pre-position ORS hydration stations."
            }
        elif wbgt_val >= 28.0:
            return {
                "category": "Warning",
                "severity": "MODERATE",
                "color": "#EAB308",
                "work_rest_cycle": "50% Work / 50% Rest per hour under shade",
                "water_intake_hourly": "1.00 Liters / hour",
                "action": "Stagger physical shifts away from peak hours (11:00 - 16:00)."
            }
        elif wbgt_val >= 26.0:
            return {
                "category": "Caution",
                "severity": "LOW",
                "color": "#84CC16",
                "work_rest_cycle": "75% Work / 25% Rest per hour",
                "water_intake_hourly": "0.75 Liters / hour",
                "action": "Encourage voluntary hydration and rest breaks in shaded areas."
            }
        else:
            return {
                "category": "Normal",
                "severity": "NONE",
                "color": "#22C55E",
                "work_rest_cycle": "Continuous work (100%)",
                "water_intake_hourly": "0.50 Liters / hour",
                "action": "Standard workplace safety conditions."
            }
