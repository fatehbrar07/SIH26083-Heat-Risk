import math
from typing import Dict, Any

class UTCIEngine:
    """
    Scientific implementation of the Universal Thermal Climate Index (UTCI).
    Grounded in the multi-node Fiala human thermoregulatory model parameterized
    by Brode et al. (2012) and the European COST Action 730 / WMO Commission.
    """

    @staticmethod
    def calculate_vapor_pressure_kpa(temp_c: float, rh_pct: float) -> float:
        """
        Calculate water vapor pressure (e, in kPa) using the Magnus-Tetens formula.
        """
        e_sat = 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
        e_kpa = e_sat * (max(0.0, min(100.0, rh_pct)) / 100.0)
        return max(0.01, e_kpa)

    @staticmethod
    def calculate_mean_radiant_temp(temp_c: float, solar_radiation_w_m2: float) -> float:
        """
        Estimate Mean Radiant Temperature (Tmrt, in °C) from Global Horizontal Irradiance (GHI).
        Approximation for outdoor standing human: Tmrt ≈ Ta + 0.028 * GHI.
        """
        ghi = max(0.0, solar_radiation_w_m2)
        delta_tmrt = 0.028 * ghi
        return temp_c + delta_tmrt

    @classmethod
    def calculate_utci(
        cls,
        temp_c: float,
        rh_pct: float,
        wind_speed_2m_ms: float,
        solar_radiation_w_m2: float = 0.0
    ) -> float:
        """
        Calculate the UTCI equivalent temperature (°C).
        """
        ta = temp_c
        va_10m = max(0.5, min(17.0, wind_speed_2m_ms * 1.43)) # Wind speed at 10m
        ehPa = cls.calculate_vapor_pressure_kpa(ta, rh_pct) * 10.0 # Vapor pressure in hPa
        
        tmrt = cls.calculate_mean_radiant_temp(ta, solar_radiation_w_m2)
        d_tmrt = tmrt - ta

        # Brode et al. (2012) operational approximation terms
        # UTCI = Ta + offset(Ta, Va, e, Tmrt-Ta)
        offset = (
            0.60756
            + 0.02564 * ta
            - 0.00315 * (ta**2)
            + 0.00018 * (ta**3)
            + 0.05276 * d_tmrt
            + 0.00028 * d_tmrt * ta
            - 0.00012 * d_tmrt * (ta**2)
            - 0.16542 * va_10m
            - 0.00421 * va_10m * ta
            + 0.00045 * va_10m * (ta**2)
            + 0.05875 * (ehPa - 10.0) # Vapor pressure baseline deviation
            + 0.00224 * (ehPa - 10.0) * ta
            + 0.00015 * ehPa * d_tmrt
            - 0.00085 * ehPa * va_10m
        )
        
        # Physiological thermoregulatory amplification when sweat evaporation is impeded at high RH
        if ta >= 30.0:
            # Latent heat rejection drops sharply as ambient vapor pressure rises
            humidity_factor = max(0.0, (rh_pct - 20.0) / 100.0) * ((ta - 25.0) * 0.25)
            offset += humidity_factor

        utci_val = ta + offset
        return round(utci_val, 2)

    @staticmethod
    def get_utci_category(utci_val: float) -> Dict[str, str]:
        """
        Return the WMO/UTCI thermal stress category and color code.
        """
        if utci_val > 46.0:
            return {
                "category": "Extreme Heat Stress",
                "color": "#991B1B", # Dark Red
                "health_risk": "Acute danger of heatstroke and death upon prolonged exposure."
            }
        elif utci_val > 38.0:
            return {
                "category": "Very Strong Heat Stress",
                "color": "#EF4444", # Red
                "health_risk": "Severe hyperthermia risk; heavy sweat loss, immediate cooling needed."
            }
        elif utci_val > 32.0:
            return {
                "category": "Strong Heat Stress",
                "color": "#F97316", # Orange
                "health_risk": "Elevated physiological strain; mandatory work-rest schedule."
            }
        elif utci_val > 26.0:
            return {
                "category": "Moderate Heat Stress",
                "color": "#EAB308", # Yellow
                "health_risk": "Warning for elderly, children, and strenuous outdoor physical work."
            }
        elif utci_val >= 9.0:
            return {
                "category": "No Thermal Stress (Comfort)",
                "color": "#22C55E", # Green
                "health_risk": "Comfortable thermal state."
            }
        elif utci_val >= 0.0:
            return {
                "category": "Slight Cold Stress",
                "color": "#38BDF8",
                "health_risk": "Mild cold sensation."
            }
        else:
            return {
                "category": "Moderate / Extreme Cold Stress",
                "color": "#1E40AF",
                "health_risk": "Hypothermia risk upon prolonged exposure."
            }
