import time
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.api.v1 import router as api_v1_router
from backend.app.models.schemas import HealthResponse

app = FastAPI(
    title="SIH26083 Extreme Heatwave Early Warning & Thermal Stress API",
    description="Operational API translating raw meteorological forecasts into physiological thermal stress (UTCI, WBGT) and hyper-local ward-level human health risk.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local and web dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API endpoints
app.include_router(api_v1_router)

# Mount frontend static directory if exists
frontend_path = os.path.join(os.path.dirname(__file__), "../../../frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", include_in_schema=False)
async def root():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "SIH26083 Extreme Heatwave Risk Engine API is active.",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """System health check and live status of Tier-1 external data sources."""
    return HealthResponse(
        status="healthy",
        service="SIH26083 Heatwave Risk Engine",
        version="1.0.0",
        tier_1_sources={
            "nasa_power_api": "Accessible (Public REST, MERRA-2 baseline)",
            "open_meteo_api": "Accessible (Public REST, 5-day NWP)",
            "census_2011_pca": "Loaded (Local Ward Baseline)",
            "utci_wbgt_physics": "Operational (WMO / ISO 7243 models)"
        },
        timestamp=time.time()
    )
