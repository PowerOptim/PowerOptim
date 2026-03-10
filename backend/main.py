from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import setup_logging, get_logger
from database import init_db
from models import User, EnergyReading, BatteryStatus

# Setup logging first thing
setup_logging(log_level="DEBUG")  # Use DEBUG for development, INFO for production
logger = get_logger(__name__)

app = FastAPI(
    title="PowerOptim API",
    description="Smart Home Energy Optimization System API",
    version="1.0.0"
)

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

@app.get("/")
async def root():
    """
    Root endpoint - health check
    """
    logger.debug("Root endpoint accessed")
    return {
        "message": "PowerOptim API is running",
        "status": "healthy"
    }

@app.get("/api/status")
async def get_status():
    """
    Get system status
    """
    logger.info("System status requested")
    return {
        "system": "online",
        "api_version": "1.0.0"
    }

# Example endpoint for dashboard data
@app.get("/api/dashboard")
async def get_dashboard_data():
    """
    Get dashboard overview data
    """
    logger.info("Dashboard data requested")
    
    # TODO: Replace with real data from Raspberry Pi
    data = {
        "powerSource": "Battery",
        "batteryLevel": 78,
        "batteryStatus": "Discharging",
        "currentPrice": "0.28",
        "priceTier": "Peak",
        "todaySavings": "2.13",
        "energyUsedToday": 18.4,
        "batteryCycles": 47,
        "systemUptime": 99.2
    }
    
    logger.debug(f"Returning dashboard data: {data}")
    return data

# Example endpoint for energy usage
@app.get("/api/energy/hourly")
async def get_hourly_energy():
    """
    Get hourly energy usage data
    """
    logger.info("Hourly energy data requested")
    
    # TODO: Replace with real data from database
    data = {
        "data": [
            {"hour": f"{i}:00", "usage": 1.5 + (i % 3) * 0.3}
            for i in range(24)
        ]
    }
    
    logger.debug(f"Returning {len(data['data'])} hourly data points")
    return data

# Example endpoint for battery info
@app.get("/api/battery")
async def get_battery_info():
    """
    Get battery status and information
    """
    logger.info("Battery info requested")
    
    # TODO: Connect to Raspberry Pi for real-time data
    data = {
        "level": 78,
        "status": "Discharging",
        "capacity": 10.0,
        "health": 98,
        "voltage": 48.2,
        "current": -2.5,
        "temperature": 25.3
    }
    
    logger.debug(f"Battery status: {data['status']}, Level: {data['level']}%")
    return data

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server with uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)