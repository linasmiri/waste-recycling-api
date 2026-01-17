from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- Collector Schemas ---
class CollectorBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=3, max_length=100)
    phone_number: str = Field(..., min_length=8, max_length=15)

class CollectorCreate(CollectorBase):
    password: str = Field(..., min_length=6)

class CollectorLogin(BaseModel):
    username: str
    password: str

class CollectorResponse(CollectorBase):
    id: int
    balance: float
    total_collected_kg: float
    created_at: datetime
    is_active: bool
    role: str
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True

class CollectorStats(BaseModel):
    total_collections: int
    total_weight_kg: float
    total_earned: float
    balance: float
    collections_by_category: dict

# --- Recyclable Item Schemas ---
class RecyclableItemBase(BaseModel):
    name: str
    category: str
    instructions: Optional[str] = None
    price_per_kg: float = 0.0

class RecyclableItemCreate(RecyclableItemBase):
    pass

class RecyclableItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    instructions: Optional[str] = None
    price_per_kg: Optional[float] = None

class RecyclableItemResponse(RecyclableItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Collection Schemas ---
class CollectionBase(BaseModel):
    item_id: int
    weight_kg: float = Field(..., gt=0)
    location: Optional[str] = None
    notes: Optional[str] = None

class CollectionCreate(CollectionBase):
    pass

class CollectionResponse(CollectionBase):
    id: int
    collector_id: int
    earned_amount: float
    collected_at: datetime
    item_name: Optional[str] = None
    item_category: Optional[str] = None

    class Config:
        from_attributes = True

# --- Transaction Schemas ---
class TransactionBase(BaseModel):
    transaction_type: str
    amount: float
    description: Optional[str] = None

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    collector_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Citizen Schemas ---
class ItemSearchQuery(BaseModel):
    query: str = Field(..., min_length=1)

class ItemSearchResponse(BaseModel):
    items: List[RecyclableItemResponse]
    query: str
    total_results: int

# --- Dashboard Schemas ---
class DashboardStats(BaseModel):
    total_collectors: int
    active_collectors: int
    total_collections: int
    total_weight_kg: float
    total_revenue: float
    collections_today: int
    top_items: List[dict]