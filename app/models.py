from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Collector(Base):
    __tablename__ = "collectors"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="collector") # "collector", "citizen", "admin"
    profile_image = Column(String, nullable=True) # Path to image
    balance = Column(Float, default=0.0)
    total_collected_kg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    collections = relationship("Collection", back_populates="collector")
    transactions = relationship("Transaction", back_populates="collector")

class RecyclableItem(Base):
    __tablename__ = "recyclable_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)  # Metal, Plastic, Glass, Paper
    instructions = Column(Text)
    price_per_kg = Column(Float, default=0.0)  # Price in local currency
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    collections = relationship("Collection", back_populates="item")

class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    collector_id = Column(Integer, ForeignKey("collectors.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("recyclable_items.id"), nullable=False)
    weight_kg = Column(Float, nullable=False)
    earned_amount = Column(Float, default=0.0)
    location = Column(String)
    notes = Column(Text)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    collector = relationship("Collector", back_populates="collections")
    item = relationship("RecyclableItem", back_populates="collections")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    collector_id = Column(Integer, ForeignKey("collectors.id"), nullable=False)
    transaction_type = Column(String, nullable=False)  # "collection", "withdrawal"
    amount = Column(Float, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    collector = relationship("Collector", back_populates="transactions")

class CitizenQuery(Base):
    __tablename__ = "citizen_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String, nullable=False)
    result_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)