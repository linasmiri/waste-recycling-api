print("--- LOADING APP.MAIN ---")
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import collectors, citizen, admin
import logging
from logging.handlers import RotatingFileHandler
import os

# --- Logging Setup ---
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

# --- Seed Database with Enhanced Recyclable Items ---
def seed_recyclable_items():
    """Populate the database with common recyclable items and prices."""
    from .database import SessionLocal
    from . import models
    
    db = SessionLocal()
    
    # Check if items already exist
    existing_count = db.query(models.RecyclableItem).count()
    if existing_count > 0:
        db.close()
        logger.info(f"Database already contains {existing_count} recyclable items")
        return
    
    # Define seed data with realistic prices (in TND - Tunisian Dinar)
    items = [
        {
            "name": "Aluminum Can",
            "category": "Metal",
            "instructions": "Rinse and flatten (optional). Remove any labels.",
            "price_per_kg": 3.5
        },
        {
            "name": "Steel Can",
            "category": "Metal",
            "instructions": "Rinse well. Cut sharp edges if opened.",
            "price_per_kg": 0.8
        },
        {
            "name": "Copper Wire",
            "category": "Metal",
            "instructions": "Strip insulation if possible. Group together.",
            "price_per_kg": 18.0
        },
        {
            "name": "Brass Fixtures",
            "category": "Metal",
            "instructions": "Remove any non-metal attachments.",
            "price_per_kg": 12.0
        },
        {
            "name": "PET Bottle (Type 1)",
            "category": "Plastic",
            "instructions": "Rinse and remove cap. Crush if possible. Look for #1 recycling symbol.",
            "price_per_kg": 0.6
        },
        {
            "name": "HDPE Bottle (Type 2)",
            "category": "Plastic",
            "instructions": "Rinse thoroughly. Remove labels if possible. Look for #2 recycling symbol.",
            "price_per_kg": 0.5
        },
        {
            "name": "Plastic Bag (LDPE)",
            "category": "Plastic",
            "instructions": "Empty contents. Clean and dry. Bundle together. Do NOT mix with other recycling.",
            "price_per_kg": 0.3
        },
        {
            "name": "Clear Glass Bottle",
            "category": "Glass",
            "instructions": "Rinse. Remove metal ring from cap. Separate by color.",
            "price_per_kg": 0.15
        },
        {
            "name": "Colored Glass Bottle",
            "category": "Glass",
            "instructions": "Rinse. Remove caps and lids. Keep separate from clear glass.",
            "price_per_kg": 0.12
        },
        {
            "name": "Cardboard Box",
            "category": "Paper",
            "instructions": "Flatten. Remove tape, staples, and Styrofoam. Keep dry.",
            "price_per_kg": 0.25
        },
        {
            "name": "Newspaper",
            "category": "Paper",
            "instructions": "Keep dry and clean. Bundle together with string.",
            "price_per_kg": 0.2
        },
        {
            "name": "Office Paper",
            "category": "Paper",
            "instructions": "Remove staples and paper clips. Keep clean and dry.",
            "price_per_kg": 0.3
        },
        {
            "name": "Mixed Paper",
            "category": "Paper",
            "instructions": "Magazines, junk mail, phone books. No food contamination.",
            "price_per_kg": 0.18
        },
        {
            "name": "E-waste - Small Electronics",
            "category": "Electronics",
            "instructions": "Phones, tablets, small devices. Remove batteries if possible.",
            "price_per_kg": 5.0
        },
        {
            "name": "Computer Parts",
            "category": "Electronics",
            "instructions": "Motherboards, RAM, hard drives. Handle carefully.",
            "price_per_kg": 8.0
        },
    ]
    
    for item_data in items:
        db_item = models.RecyclableItem(**item_data)
        db.add(db_item)
    
    db.commit()
    db.close()
    logger.info(f"Successfully seeded {len(items)} recyclable items into database")

# Seed the database
seed_recyclable_items()

# --- App Setup ---
app = FastAPI(
    title="Waste Sorting & Recycling Optimization API",
    description="API for Barbecha (collector) onboarding and Citizen waste sorting assistance.",
    version="2.0.0",
    contact={
        "name": "Waste Management Team",
        "email": "support@wasteapp.tn"
    }
)

# Static Files (Images)
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_origin_regex=".*", # Allows any origin (including null for files)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(collectors.router)
app.include_router(citizen.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Waste Sorting & Recycling Optimization API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "collectors": "/collectors",
            "citizen": "/citizen",
            "admin": "/admin"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2025-01-17"}