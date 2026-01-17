from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Collector(Base):
    __tablename__ = "collectors"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    phone_number = Column(String)
    hashed_password = Column(String)  # For JWT auth
    balance = Column(Float, default=0.0)

    transactions = relationship("Transaction", back_populates="collector")

    transactions = relationship("Transaction", back_populates="collector")

class Transaction(Base):
    """Fair-payment ledger: Records materials collected and paid for."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    collector_id = Column(Integer, ForeignKey("collectors.id"))
    material_type = Column(String) # e.g., "Plastic", "Metal"
    weight_kg = Column(Float)
    amount_paid = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    collector = relationship("Collector", back_populates="transactions")

class RecyclableItem(Base):
    """Database of items for the Citizen Assistant search."""
    __tablename__ = "recyclable_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # e.g., "Coke Bottle"
    category = Column(String) # e.g., "Plastic"
    instructions = Column(String) # e.g., "Rinse and remove cap"

class DropOffPoint(Base):
    """Locations where citizens can drop items."""
    __tablename__ = "drop_off_points"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    accepted_categories = Column(String) # Comma-separated or JSON
