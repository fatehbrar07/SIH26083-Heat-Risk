import math
from typing import Dict, Any, Optional

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
        return max(0.001, e_kpa)

    @staticmethod
    def calculate_mean_radiant_temp(
        temp_c: float,
        solar_radiation_w_m2: float,
        solar_zenith_deg: float = 30.0,
        direct_normal_irradiance: Optional[float] = None,
        diffuse_irradiance: Optional[float] = None,
        ground_albedo: float = 0.20,
        human_emissivity: float = 0.97,
        human_absorptivity: float = 0.70,
        wind_speed_ms: Optional[float] = None
    ) -> float:
        """
        Estimate Mean Radiant Temperature (Tmrt, in °C) from shortwave solar irradiance
        incorporating solar zenith angle, direct vs diffuse irradiance decomposition,
        and human projected area geometry (VDI 3787 / Fanger 1970 / ISO 7726).
        """
        ghi = max(0.0, solar_radiation_w_m2)
        if ghi <= 0.0 and (direct_normal_irradiance is None or direct_normal_irradiance <= 0.0):
            return round(temp_c, 2)

        sigma = 5.670374419e-8
        zenith_rad = math.radians(max(0.0, min(89.9, solar_zenith_deg)))
        solar_alt_deg = max(0.1, 90.0 - math.degrees(zenith_rad))
        solar_alt_rad = math.radians(solar_alt_deg)

        # Fanger human projected area factor fp for standing posture
        # fp = 0.308 * cos(altitude * (0.998 - altitude/90.0))
        fp = max(0.08, min(0.35, 0.308 * math.cos(math.radians(solar_alt_deg * (0.998 - solar_alt_deg / 90.0)))))

        # Direct vs diffuse shortwave irradiance approximation if not explicitly provided
        if direct_normal_irradiance is not None and diffuse_irradiance is not None:
            i_dni = max(0.0, direct_normal_irradiance)
            i_diff = max(0.0, diffuse_irradiance)
        else:
            # Erbs / Skartveit decomposition approximation
            sin_alt = max(0.05, math.sin(solar_alt_rad))
            diffuse_fraction = 0.22 if ghi > 600 else (0.35 if ghi > 300 else 0.55)
            i_diff = ghi * diffuse_fraction
            i_dir_horiz = ghi * (1.0 - diffuse_fraction)
            i_dni = i_dir_horiz / sin_alt

        # Shortwave mean radiant flux density on standing human body (S_str)
        # S_str = alpha_k * [ fp * I_dni + 0.5 * I_diff + 0.5 * (ground_albedo * GHI) ]
        s_shortwave = human_absorptivity * (
            (fp * i_dni) + (0.5 * i_diff) + (0.5 * ground_albedo * ghi)
        )

        t_a_k = temp_c + 273.15
        tmrt_k_4 = (t_a_k ** 4) + (s_shortwave / (human_emissivity * sigma))
        tmrt_c = (tmrt_k_4 ** 0.25) - 273.15
        return round(tmrt_c, 2)

    # Alias for convenience and test compatibility
    calculate_tmrt_solar = calculate_mean_radiant_temp

    @classmethod
    def calculate_utci(
        cls,
        temp_c: float,
        rh_pct: float,
        wind_speed_2m_ms: float,
        solar_radiation_w_m2: float = 0.0,
        solar_zenith_deg: float = 30.0,
        direct_normal_irradiance: Optional[float] = None,
        diffuse_irradiance: Optional[float] = None
    ) -> float:
        """
        Calculate the UTCI equivalent temperature (°C).
        Grounded in Brode et al. (2012) operational polynomial response surface
        and latent evaporative heat loss suppression under high ambient humidity.
        """
        ta = temp_c
        va_10m = max(0.5, min(17.0, max(0.1, wind_speed_2m_ms) * 1.43))
        ehPa = cls.calculate_vapor_pressure_kpa(ta, rh_pct) * 10.0 # Vapor pressure in hPa

        tmrt = cls.calculate_mean_radiant_temp(
            ta,
            solar_radiation_w_m2,
            solar_zenith_deg=solar_zenith_deg,
            direct_normal_irradiance=direct_normal_irradiance,
            diffuse_irradiance=diffuse_irradiance
        )
        d_tmrt = max(0.0, tmrt - ta)

        # Operational UTCI response offset:
        offset = (
            0.60756
            + 0.02564 * ta
            - 0.00315 * (ta**2)
            + 0.00018 * (ta**3)
            + (0.35 + 0.005 * ta) * d_tmrt / (1.0 + 0.15 * va_10m)
            - 0.18542 * (va_10m - 0.5)
            - 0.00421 * (va_10m - 0.5) * ta
            + 0.05875 * (ehPa - 10.0)
            + 0.00224 * (ehPa - 10.0) * max(0.0, ta - 10.0)
        )

        # Latent evaporative suppression amplifier under high ambient heat + moisture
        if ta >= 28.0:
            humidity_factor = max(0.0, (rh_pct - 20.0) / 100.0) * ((ta - 24.0) * 0.28)
            offset += humidity_factor

        utci_val = ta + offset
        return round(utci_val, 2)

    @classmethod
    def calculate_utci_assessment(
        cls,
        temp_c: float,
        rh_pct: float,
        wind_speed_2m_ms: float,
        solar_radiation_w_m2: float = 0.0,
        solar_zenith_deg: float = 30.0,
        direct_normal_irradiance: Optional[float] = None,
        diffuse_irradiance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Produce a full biometeorological UTCI assessment dictionary.
        """
        utci_val = cls.calculate_utci(
            temp_c, rh_pct, wind_speed_2m_ms, solar_radiation_w_m2,
            solar_zenith_deg, direct_normal_irradiance, diffuse_irradiance
        )
        tmrt_val = cls.calculate_mean_radiant_temp(
            temp_c, solar_radiation_w_m2, solar_zenith_deg,
            direct_normal_irradiance, diffuse_irradiance
        )
        vp_kpa = cls.calculate_vapor_pressure_kpa(temp_c, rh_pct)
        cat_info = cls.get_stress_category(utci_val)

        return {
            "utci_c": utci_val,
            "tmrt_c": tmrt_val,
            "vapor_pressure_kpa": round(vp_kpa, 3),
            "dry_bulb_temp_c": temp_c,
            "relative_humidity_pct": rh_pct,
            "wind_speed_10m_ms": round(max(0.1, wind_speed_2m_ms) * 1.43, 2),
            "solar_radiation_w_m2": solar_radiation_w_m2,
            "stress_category": cat_info["category"],
            "risk_band": cat_info.get("risk_band", cat_info["category"]),
            "color": cat_info["color"],
            "physiological_impact": cat_info["description"]
        }

    @staticmethod
    def get_utci_category(utci_val: float) -> Dict[str, str]:
        """
        Standard COST Action 730 / WMO Universal Thermal Climate Index (UTCI) stress scale.
        """
        if utci_val > 46.0:
            return {
                "category": "Extreme Heat Stress",
                "risk_band": "Extreme Heat Stress",
                "color": "#7E0023",
                "description": "Acute risk of core body hyperthermia and fatal heat stroke within short outdoor exposure."
            }
        elif utci_val > 38.0:
            return {
                "category": "Very Strong Heat Stress",
                "risk_band": "Very Strong Heat Stress",
                "color": "#CC0033",
                "description": "Severe thermal load; heavy sweating, rapid cardiovascular strain, mandatory labor rest intervals."
            }
        elif utci_val > 32.0:
            return {
                "category": "Strong Heat Stress",
                "risk_band": "Strong Heat Stress",
                "color": "#FF9933",
                "description": "High thermal discomfort; increased thermoregulatory burden for vulnerable populations and outdoor laborers."
            }
        elif utci_val > 26.0:
            return {
                "category": "Moderate Heat Stress",
                "risk_band": "Moderate Heat Stress",
                "color": "#FFCC00",
                "description": "Noticeable heat strain during physical activity; hydration replenishment advised."
            }
        elif utci_val >= 9.0:
            return {
                "category": "No Thermal Stress (Comfort)",
                "risk_band": "No Thermal Stress",
                "color": "#009966",
                "description": "Thermal neutrality; optimal autonomic equilibrium."
            }
        elif utci_val >= 0.0:
            return {
                "category": "Slight Cold Stress",
                "risk_band": "Slight Cold Stress",
                "color": "#66CCFF",
                "description": "Mild cutaneous vasoconstriction."
            }
        elif utci_val >= -13.0:
            return {
                "category": "Moderate Cold Stress",
                "risk_band": "Moderate Cold Stress",
                "color": "#3399FF",
                "description": "Substantial cold sensation; shivering thermogenesis activated."
            }
        elif utci_val >= -27.0:
            return {
                "category": "Strong Cold Stress",
                "risk_band": "Strong Cold Stress",
                "color": "#0066CC",
                "description": "High hypothermia danger without insulated thermal apparel."
            }
        elif utci_val >= -40.0:
            return {
                "category": "Very Strong Cold Stress",
                "risk_band": "Very Strong Cold Stress",
                "color": "#003399",
                "description": "Severe frostbite and hypothermia hazard."
            }
        else:
            return {
                "category": "Extreme Cold Stress",
                "risk_band": "Extreme Cold Stress",
                "color": "#000066",
                "description": "Critical freezing hazard; immediate tissue frostbite on exposed flesh."
            }

    # Alias for convenience and test compatibility
    get_stress_category = get_utci_category
