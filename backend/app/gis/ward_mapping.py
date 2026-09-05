import os
import json
from typing import Dict, Any, List, Optional
from backend.app.risk.risk_engine import RiskEngine
from backend.app.vulnerability.hvi_engine import SUPPORTED_CITIES, HVIEngine

class GISEngine:
    """
    GIS and Spatial Attribution Engine.
    Handles multi-city GeoJSON parsing, ward spatial polygon attribution, and joining
    meteorological risk layers without claiming fake ward-level NWP resolution.
    """

    def __init__(
        self,
        geojson_path: str | None = None,
        city_id: str = "delhi"
    ):
        base_dir = os.path.dirname(__file__)
        self.sample_dir: str = os.path.join(base_dir, "../../../data/sample")
        self.risk_engine = RiskEngine()
        self.hvi_engine = self.risk_engine.hvi_engine

        # Multi-city geojson cache: {city_id: geojson_dict}
        self._city_geojson_cache: Dict[str, Dict[str, Any]] = {}
        self.city_id: str = self.hvi_engine._normalize_city_id(city_id)
        self.geojson_path = geojson_path

        # Load all default geojson layers
        self._load_all_geojsons()

        # If custom path provided, override for current city
        if geojson_path and os.path.exists(geojson_path):
            with open(geojson_path, "r") as f:
                self._city_geojson_cache[self.city_id] = json.load(f)

    def _load_all_geojsons(self):
        """Load GeoJSON boundary files for all supported cities into memory cache."""
        for cid, meta in SUPPORTED_CITIES.items():
            filepath = os.path.join(self.sample_dir, meta["geojson_file"])
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    self._city_geojson_cache[cid] = json.load(f)
            else:
                self._city_geojson_cache[cid] = {"type": "FeatureCollection", "features": []}

    @property
    def raw_geojson(self) -> Dict[str, Any]:
        """Backward-compatible property returning GeoJSON for default/current city."""
        return self._city_geojson_cache.get(self.city_id, {"type": "FeatureCollection", "features": []})

    def get_geojson_for_city(self, city_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve raw GeoJSON FeatureCollection for specified city."""
        target_city = self.hvi_engine._normalize_city_id(city_id) if city_id else self.city_id
        return self._city_geojson_cache.get(target_city, {"type": "FeatureCollection", "features": []})

    def generate_risk_geojson(
        self,
        temp_c: float,
        rh_pct: float,
        wind_speed_ms: float,
        solar_radiation_w_m2: float = 0.0,
        consecutive_extreme_days: int = 1,
        city_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an enriched GeoJSON FeatureCollection with computed risk properties for each ward
        in the target city.
        """
        target_city = self.hvi_engine._normalize_city_id(city_id) if city_id else self.city_id
        city_meta = SUPPORTED_CITIES.get(target_city, SUPPORTED_CITIES["delhi"])
        raw_geo = self.get_geojson_for_city(target_city)

        enriched_features = []
        for feature in raw_geo.get("features", []):
            props = feature.get("properties", {})
            ward_id = props.get("ward_id")

            # Compute composite risk for this ward (RiskEngine will resolve city from ward_id/hvi)
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
                "city_id": target_city,
                "city_name": city_meta["city_name"],
                "risk_score": risk_data["risk_score"],
                "risk_band": risk_data["risk_band"],
                "risk_color": risk_data["risk_color"],
                "action_priority": risk_data["action_priority"],
                "hazard_score": risk_data["hazard_score"],
                "vulnerability_score": risk_data["vulnerability_score"],
                "hvi_score": risk_data["vulnerability_score"],
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
            "name": f"{target_city.title()}_Enriched_Heatwave_Risk_Wards",
            "crs": raw_geo.get("crs"),
            "features": enriched_features,
            "metadata": {
                "city_id": target_city,
                "city_name": city_meta["city_name"],
                "total_wards": len(enriched_features),
                "environmental_input": {
                    "temperature_c": temp_c,
                    "relative_humidity_pct": rh_pct,
                    "wind_speed_ms": wind_speed_ms,
                    "solar_radiation_w_m2": solar_radiation_w_m2
                },
                "spatial_note": f"Meteorological inputs spatially downscaled across {city_meta['city_name']} municipal administrative ward polygons with Census 2011 vulnerability weighting."
            }
        }
