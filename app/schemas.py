from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Collector Schemas ---
class CollectorBase(BaseModel):
    username: str
    full_name: str
    phone_number: str

class CollectorCreate(CollectorBase):
    password: str

class Collector(CollectorBase):
    id: int
    balance: float
    class Config:
        orm_mode = True

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Transaction Schemas ---
class TransactionCreate(BaseModel):
    material_type: str
    weight_kg: float
    price_per_kg: float 

class Transaction(BaseModel):
    id: int
    material_type: str
    weight_kg: float
    amount_paid: float
    timestamp: datetime
    class Config:
        orm_mode = True

# --- Citizen/Item Schemas ---
class ItemBase(BaseModel):
    name: str
    category: str
    instructions: str

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        orm_mode = True

class DropOffPointBase(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    accepted_categories: str

class DropOffPointCreate(DropOffPointBase):
    pass

class DropOffPoint(DropOffPointBase):
    id: int
    class Config:
        orm_mode = True
