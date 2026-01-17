print("--- LOADING APP.MAIN ---")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import collectors, citizen
import logging
from logging.handlers import RotatingFileHandler
import os

# --- Logging Setup (The "Flags") ---
# Determine logging path: use "logs" directory at project root
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file_path = os.path.join(log_dir, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(log_file_path, maxBytes=1000000, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("waste_app")

# --- Database Setup ---
Base.metadata.create_all(bind=engine)

# --- Seed Database with Recyclable Items ---
def seed_recyclable_items():
    """Populate the database with common recyclable items."""
    from .database import SessionLocal
    db = SessionLocal()
    
    # Check if items already exist
    if db.query(Base.metadata.tables['recyclable_items']).count() > 0:
        db.close()
        return
    
    # Define seed data
    items = [
        {
            "name": "Aluminum Can",
            "category": "Metal",
            "instructions": "Rinse and flatten (optional). Remove any labels."
        },
        {
            "name": "Steel Can",
            "category": "Metal",
            "instructions": "Rinse well. Cut sharp edges if opened."
        },
        {
            "name": "Copper Wire",
            "category": "Metal",
            "instructions": "Strip insulation if possible. Group together."
        },
        {
            "name": "Coke Bottle",
            "category": "Plastic",
            "instructions": "Rinse and remove cap. Crush if possible."
        },
        {
            "name": "Plastic Bag",
            "category": "Plastic",
            "instructions": "Empty contents. Do NOT put in recycling bin (tangles machinery)."
        },
        {
            "name": "Glass Bottle",
            "category": "Glass",
            "instructions": "Rinse. Remove metal ring from cap."
        },
        {
            "name": "Cardboard Box",
            "category": "Paper",
            "instructions": "Flatten. Remove tape and Styrofoam."
        },
    ]
    
    from . import models
    for item_data in items:
        db_item = models.RecyclableItem(**item_data)
        db.add(db_item)
    
    db.commit()
    db.close()
    logger.info("Recyclable items database seeded successfully")

seed_recyclable_items()

# --- App Setup ---
app = FastAPI(
    title="Waste Sorting & Recycling Optimization API",
    description="API for Barbecha onboarding and Citizen waste sorting assistance.",
    version="1.0.0"
)

# CORS (Allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ALLOW ALL ORIGINS FOR DEMO
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(collectors.router)
app.include_router(citizen.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Waste Sorting & Recycling Optimization API", "docs": "/docs"}
