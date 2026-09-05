import math
from typing import Dict, Any

class HeatIndexEngine:
    """
    Standard NOAA National Weather Service (NWS) Heat Index calculation
    via Rothfusz regression equation with Steadman corrections.
    Retained in SIH26083 as a comparative baseline.
    """

    @classmethod
    def calculate_heat_index(cls, temp_c: float, rh_pct: float) -> float:
        """
        Calculate NOAA Heat Index in °C.
        """
        # Heat index is typically computed in Fahrenheit
        tf = (temp_c * 9.0 / 5.0) + 32.0
        rh = max(0.0, min(100.0, rh_pct))

        # Simple Steadman equation for low heat
        hi_simple = 0.5 * (tf + 61.0 + ((tf - 68.0) * 1.2) + (rh * 0.094))

        if hi_simple >= 80.0:
            # Full Rothfusz polynomial regression
            hi_f = (
                -42.379
                + 2.04901523 * tf
                + 10.14333127 * rh
                - 0.22475541 * tf * rh
                - 0.00683783 * tf * tf
                - 0.05481717 * rh * rh
                + 0.00122874 * tf * tf * rh
                + 0.00085282 * tf * rh * rh
                - 0.00000199 * tf * tf * rh * rh
            )

            # Adjustment for low humidity
            if rh < 13.0 and 80.0 <= tf <= 112.0:
                adj = ((13.0 - rh) / 4.0) * math.sqrt((17.0 - abs(tf - 95.0)) / 17.0)
                hi_f -= adj
            # Adjustment for high humidity
            elif rh > 85.0 and 80.0 <= tf <= 87.0:
                adj = ((rh - 85.0) / 10.0) * ((87.0 - tf) / 5.0)
                hi_f += adj
        else:
            hi_f = hi_simple

        # Convert back to Celsius
        hi_c = (hi_f - 32.0) * 5.0 / 9.0
        return round(hi_c, 2)

    @staticmethod
    def get_heat_index_category(hi_val: float) -> Dict[str, str]:
        if hi_val >= 51.0:
            return {"category": "Extreme Danger", "color": "#EF4444", "description": "Heatstroke imminent."}
        elif hi_val >= 39.0:
            return {"category": "Danger", "color": "#F97316", "description": "Heat exhaustion likely."}
        elif hi_val >= 32.0:
            return {"category": "Extreme Caution", "color": "#EAB308", "description": "Fatigue possible with prolonged exposure."}
        elif hi_val >= 27.0:
            return {"category": "Caution", "color": "#84CC16", "description": "Mild fatigue possible."}
        else:
            return {"category": "Normal", "color": "#22C55E", "description": "Apparent temperature within normal comfort limits."}
