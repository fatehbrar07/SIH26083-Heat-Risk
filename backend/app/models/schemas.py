from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class WeatherCurrentRequest(BaseModel):
    temperature_c: float = Field(default=40.0, description="2m air temperature in Celsius")
    relative_humidity_pct: float = Field(default=35.0, description="Relative humidity (0-100%)")
    wind_speed_ms: float = Field(default=2.5, description="Wind speed in m/s")
    solar_radiation_w_m2: float = Field(default=650.0, description="Global Horizontal Solar Irradiance in W/m^2")

class ThermalCalculateRequest(BaseModel):
    temperature_c: float = Field(..., description="Air temperature in Celsius")
    relative_humidity_pct: float = Field(..., description="Relative humidity (0-100%)")
    wind_speed_ms: float = Field(default=2.5, description="Wind speed in m/s")
    solar_radiation_w_m2: float = Field(default=600.0, description="Solar irradiance in W/m^2")

class RiskCalculateRequest(BaseModel):
    ward_id: str = Field(default="DEL-W01", description="Ward Identifier (e.g. DEL-W01)")
    temperature_c: float = Field(default=40.0, description="Air temperature in Celsius")
    relative_humidity_pct: float = Field(default=35.0, description="Relative humidity (0-100%)")
    wind_speed_ms: float = Field(default=2.5, description="Wind speed in m/s")
    solar_radiation_w_m2: float = Field(default=650.0, description="Solar irradiance in W/m^2")
    consecutive_extreme_days: int = Field(default=1, description="Number of consecutive extreme heat days")

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    tier_1_sources: Dict[str, str]
    timestamp: float
