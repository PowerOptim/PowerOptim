from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from utils import setup_logging, get_logger
from database import init_db
from models import User, SensorReading, DayAheadLMP, RealtimeLMP
from routes import battery, cost, dashboard, energy, system, pi

# Setup logging first thing
setup_logging(log_level="DEBUG")  # Use DEBUG for development, INFO for production
logger = get_logger(__name__)

app = FastAPI(
    title="PowerOptim API",
    description="Smart Home Energy Optimization System API",
    version="1.0.0"
)

# Mounting all the routers
api_router = APIRouter(prefix="/api")
api_router.include_router(dashboard.router)
api_router.include_router(battery.router)
api_router.include_router(cost.router)
api_router.include_router(energy.router)
api_router.include_router(system.router)
api_router.include_router(pi.router)
app.include_router(api_router)

# CORS configuration - allows your Vue frontend to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Default Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://localhost:8080",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 PowerOptim API starting up...")
    init_db()
    logger.info("Environment: Development")
    logger.info("API docs available at: /docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 PowerOptim API shutting down...")
