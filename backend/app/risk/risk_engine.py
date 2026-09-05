import os
import yaml
from typing import Dict, Any, List
from backend.app.thermal.utci_engine import UTCIEngine
from backend.app.thermal.wbgt_engine import WBGTEngine
from backend.app.vulnerability.hvi_engine import HVIEngine

class RiskEngine:
    """
    Composite Human Heat-Health Risk Engine.
    Integrates:
    - Physiological Thermal Stress (Hazard Score: 0-100 derived from UTCI & WBGT)
    - Socio-Demographic Vulnerability (HVI Score: 0-100)
    - Multi-Day Persistence / Exposure Duration Multiplier
    
    Generates an honest, relative heat-health risk score (0-100) without fabricated death counts.
    """

    def __init__(self, config_path: str | None = None, thresholds_path: str | None = None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "../../../config/risk_weights.yaml")
        if not thresholds_path:
            thresholds_path = os.path.join(os.path.dirname(__file__), "../../../config/thresholds.yaml")

        self.config_path: str = config_path
        self.thresholds_path: str = thresholds_path
        self.hazard_weight, self.vuln_weight, self.duration_mult = self._load_risk_weights()
        self.risk_bands = self._load_risk_bands()
        self.hvi_engine = HVIEngine()

    def _load_risk_weights(self) -> tuple[float, float, Dict[str, float]]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                cfg = yaml.safe_load(f).get("risk_matrix", {})
                return (
                    cfg.get("hazard_weight", 0.60),
                    cfg.get("vulnerability_weight", 0.40),
                    cfg.get("duration_multiplier", {
                        "day_1": 1.0, "day_2": 1.10, "day_3": 1.20, "day_4_plus": 1.30
                    })
                )
        return 0.60, 0.40, {"day_1": 1.0, "day_2": 1.10, "day_3": 1.20, "day_4_plus": 1.30}

    def _load_risk_bands(self) -> Dict[str, Any]:
        if os.path.exists(self.thresholds_path):
            with open(self.thresholds_path, "r") as f:
                return yaml.safe_load(f).get("risk_bands", {})
        return {}

    def calculate_hazard_score(self, utci_val: float, wbgt_val: float) -> float:
        """
        Normalize physiological thermal stress (UTCI & WBGT) into a 0 - 100 Hazard Score.
        - UTCI 26°C (Threshold of Heat Stress) -> Hazard Score 20
        - UTCI 38°C (Very Strong Heat Stress)  -> Hazard Score 65
        - UTCI 46°C+ (Extreme Danger)          -> Hazard Score 95-100
        """
        # Primary mapping from UTCI
        if utci_val <= 20.0:
            utci_score = 0.0
        elif utci_val <= 26.0:
            utci_score = ((utci_val - 20.0) / 6.0) * 20.0
        elif utci_val <= 32.0:
            utci_score = 20.0 + ((utci_val - 26.0) / 6.0) * 25.0 # 20 to 45
        elif utci_val <= 38.0:
            utci_score = 45.0 + ((utci_val - 32.0) / 6.0) * 25.0 # 45 to 70
        elif utci_val <= 46.0:
            utci_score = 70.0 + ((utci_val - 38.0) / 8.0) * 20.0 # 70 to 90
        else:
            utci_score = 90.0 + min(10.0, (utci_val - 46.0) * 2.5) # 90 to 100

        # Secondary occupational reinforcement from WBGT
        if wbgt_val >= 32.0:
            wbgt_score = 95.0
        elif wbgt_val >= 30.0:
            wbgt_score = 75.0 + ((wbgt_val - 30.0) / 2.0) * 20.0
        elif wbgt_val >= 28.0:
            wbgt_score = 50.0 + ((wbgt_val - 28.0) / 2.0) * 25.0
        elif wbgt_val >= 26.0:
            wbgt_score = 25.0 + ((wbgt_val - 26.0) / 2.0) * 25.0
        else:
            wbgt_score = max(0.0, wbgt_val)

        # Blended physiological hazard score (70% UTCI general + 30% WBGT occupational)
        blended = (0.70 * utci_score) + (0.30 * wbgt_score)
        return round(min(100.0, max(0.0, blended)), 1)

    def calculate_risk(
        self,
        ward_id: str,
        temp_c: float,
        rh_pct: float,
        wind_speed_2m_ms: float,
        solar_radiation_w_m2: float = 0.0,
        consecutive_extreme_days: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate final Composite Relative Heat-Health Risk Score for a given ward and weather scenario.
        """
        # 1. Thermal Calculations
        utci_val = UTCIEngine.calculate_utci(temp_c, rh_pct, wind_speed_2m_ms, solar_radiation_w_m2)
        wbgt_val = WBGTEngine.calculate_outdoor_wbgt(temp_c, rh_pct, wind_speed_2m_ms, solar_radiation_w_m2)
        utci_meta = UTCIEngine.get_utci_category(utci_val)
        wbgt_meta = WBGTEngine.get_occupational_advisory(wbgt_val)

        # 2. Hazard Score (0-100)
        hazard_score = self.calculate_hazard_score(utci_val, wbgt_val)

        # 3. Ward Vulnerability Score (0-100)
        ward_hvi = self.hvi_engine.calculate_ward_hvi(ward_id)
        vuln_score = ward_hvi.get("hvi_score", 50.0)

        # 4. Multi-Day Duration Factor
        if consecutive_extreme_days >= 4:
            dur_mult = self.duration_mult.get("day_4_plus", 1.30)
        elif consecutive_extreme_days == 3:
            dur_mult = self.duration_mult.get("day_3", 1.20)
        elif consecutive_extreme_days == 2:
            dur_mult = self.duration_mult.get("day_2", 1.10)
        else:
            dur_mult = self.duration_mult.get("day_1", 1.00)

        # 5. Composite Risk Calculation
        raw_composite = (self.hazard_weight * hazard_score) + (self.vuln_weight * vuln_score)
        final_risk = round(min(100.0, raw_composite * dur_mult), 1)

        # 6. Categorization into NDMA-aligned Risk Bands
        if final_risk >= 80.0:
            band_key = "very_high"
        elif final_risk >= 55.0:
            band_key = "high"
        elif final_risk >= 30.0:
            band_key = "moderate"
        else:
            band_key = "low"

        band_info = self.risk_bands.get(band_key, {
            "label": "Moderate", "color": "#EAB308", "action_priority": "Precautionary Advisory"
        })

        return {
            "ward_id": ward_id,
            "ward_name": ward_hvi.get("ward_name"),
            "risk_score": final_risk,
            "risk_band": band_info.get("label"),
            "risk_color": band_info.get("color"),
            "action_priority": band_info.get("action_priority"),
            "hazard_score": hazard_score,
            "vulnerability_score": vuln_score,
            "thermal_metrics": {
                "air_temperature_c": temp_c,
                "relative_humidity_pct": rh_pct,
                "wind_speed_ms": wind_speed_2m_ms,
                "solar_radiation_w_m2": solar_radiation_w_m2,
                "utci_c": utci_val,
                "utci_category": utci_meta.get("category"),
                "wbgt_c": wbgt_val,
                "wbgt_category": wbgt_meta.get("category")
            },
            "duration_multiplier_applied": dur_mult,
            "demographic_context": ward_hvi.get("demographic_summary"),
            "disclaimer": "Prototype relative risk estimate — not a clinical or mortality forecast."
        }
