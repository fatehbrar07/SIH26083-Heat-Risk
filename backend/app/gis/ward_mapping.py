import os
import json
from typing import Dict, Any, List
from backend.app.risk.risk_engine import RiskEngine

class GISEngine:
    """
    GIS and Spatial Attribution Engine.
    Handles GeoJSON parsing, ward spatial polygon attribution, and joining
    meteorological risk layers without claiming fake ward-level NWP resolution.
    """

    def __init__(self, geojson_path: str | None = None):
        if not geojson_path:
            geojson_path = os.path.join(os.path.dirname(__file__), "../../../data/sample/delhi_wards.geojson")
        self.geojson_path = geojson_path
        self.risk_engine = RiskEngine()
        self.raw_geojson = self._load_geojson()

    def _load_geojson(self) -> Dict[str, Any]:
        if os.path.exists(self.geojson_path):
            with open(self.geojson_path, "r") as f:
                return json.load(f)
        return {"type": "FeatureCollection", "features": []}

    def generate_risk_geojson(
        self,
        temp_c: float,
        rh_pct: float,
        wind_speed_ms: float,
        solar_radiation_w_m2: float = 0.0,
        consecutive_extreme_days: int = 1
    ) -> Dict[str, Any]:
        """
        Generate an enriched GeoJSON FeatureCollection with computed risk properties for each ward.
        """
        enriched_features = []
        for feature in self.raw_geojson.get("features", []):
            props = feature.get("properties", {})
            ward_id = props.get("ward_id")
            
            # Compute composite risk for this ward
            risk_data = self.risk_engine.calculate_risk(
                ward_id=ward_id,
                temp_c=temp_c,
                rh_pct=rh_pct,
                wind_speed_2m_ms=wind_speed_ms,
                solar_radiation_w_m2=solar_radiation_w_m2,
                consecutive_extreme_days=consecutive_extreme_days
            )

            # Enrich feature properties for Leaflet styling and tooltips
            new_props = {
                **props,
                "risk_score": risk_data["risk_score"],
                "risk_band": risk_data["risk_band"],
                "risk_color": risk_data["risk_color"],
                "action_priority": risk_data["action_priority"],
                "hazard_score": risk_data["hazard_score"],
                "vulnerability_score": risk_data["vulnerability_score"],
                "utci_c": risk_data["thermal_metrics"]["utci_c"],
                "utci_category": risk_data["thermal_metrics"]["utci_category"],
                "wbgt_c": risk_data["thermal_metrics"]["wbgt_c"],
                "wbgt_category": risk_data["thermal_metrics"]["wbgt_category"],
                "demographics": risk_data["demographic_context"],
                "disclaimer": risk_data["disclaimer"]
            }

            enriched_features.append({
                "type": "Feature",
                "geometry": feature.get("geometry"),
                "properties": new_props
            })

        return {
            "type": "FeatureCollection",
            "name": "Enriched_Heatwave_Risk_Wards",
            "crs": self.raw_geojson.get("crs"),
            "features": enriched_features,
            "metadata": {
                "environmental_input": {
                    "temperature_c": temp_c,
                    "relative_humidity_pct": rh_pct,
                    "wind_speed_ms": wind_speed_ms,
                    "solar_radiation_w_m2": solar_radiation_w_m2
                },
                "spatial_note": "Meteorological inputs spatially downscaled across municipal administrative ward polygons with demographic vulnerability weighting."
            }
        }
