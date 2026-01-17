from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# Note: In production, add proper admin authentication
# For now, these endpoints are open for testing

@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overall system statistics"""
    # Total collectors
    total_collectors = db.query(models.Collector).count()
    active_collectors = db.query(models.Collector).filter(
        models.Collector.is_active == True
    ).count()
    
    # Total collections
    total_collections = db.query(models.Collection).count()
    
    # Total weight and revenue
    collection_stats = db.query(
        func.sum(models.Collection.weight_kg).label("total_weight"),
        func.sum(models.Collection.earned_amount).label("total_revenue")
    ).first()
    
    # Collections today
    today = datetime.utcnow().date()
    collections_today = db.query(models.Collection).filter(
        func.date(models.Collection.collected_at) == today
    ).count()
    
    # Top items by collection count
    top_items = db.query(
        models.RecyclableItem.name,
        models.RecyclableItem.category,
        func.count(models.Collection.id).label("collection_count"),
        func.sum(models.Collection.weight_kg).label("total_weight")
    ).join(
        models.Collection, models.Collection.item_id == models.RecyclableItem.id
    ).group_by(
        models.RecyclableItem.id
    ).order_by(
        func.count(models.Collection.id).desc()
    ).limit(5).all()
    
    return {
        "total_collectors": total_collectors,
        "active_collectors": active_collectors,
        "total_collections": total_collections,
        "total_weight_kg": float(collection_stats.total_weight or 0),
        "total_revenue": float(collection_stats.total_revenue or 0),
        "collections_today": collections_today,
        "top_items": [
            {
                "name": item.name,
                "category": item.category,
                "collection_count": item.collection_count,
                "total_weight_kg": float(item.total_weight or 0)
            }
            for item in top_items
        ]
    }

@router.get("/collectors", response_model=List[schemas.CollectorResponse])
def get_all_collectors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all collectors"""
    collectors = db.query(models.Collector).offset(skip).limit(limit).all()
    return collectors

@router.get("/collectors/{collector_id}", response_model=schemas.CollectorResponse)
def get_collector_by_id(collector_id: int, db: Session = Depends(get_db)):
    """Get specific collector by ID"""
    collector = db.query(models.Collector).filter(
        models.Collector.id == collector_id
    ).first()
    
    if not collector:
        raise HTTPException(status_code=404, detail="Collector not found")
    
    return collector

@router.post("/items", response_model=schemas.RecyclableItemResponse, status_code=status.HTTP_201_CREATED)
def create_recyclable_item(
    item: schemas.RecyclableItemCreate,
    db: Session = Depends(get_db)
):
    """Create a new recyclable item"""
    # Check if item already exists
    existing_item = db.query(models.RecyclableItem).filter(
        models.RecyclableItem.name == item.name
    ).first()
    
    if existing_item:
        raise HTTPException(status_code=400, detail="Item already exists")
    
    new_item = models.RecyclableItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item

@router.put("/items/{item_id}", response_model=schemas.RecyclableItemResponse)
def update_recyclable_item(
    item_id: int,
    item_update: schemas.RecyclableItemUpdate,
    db: Session = Depends(get_db)
):
    """Update a recyclable item"""
    item = db.query(models.RecyclableItem).filter(
        models.RecyclableItem.id == item_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update fields
    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    
    return item

@router.delete("/items/{item_id}")
def delete_recyclable_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a recyclable item"""
    item = db.query(models.RecyclableItem).filter(
        models.RecyclableItem.id == item_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if item has collections
    has_collections = db.query(models.Collection).filter(
        models.Collection.item_id == item_id
    ).first()
    
    if has_collections:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete item with existing collections"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item deleted successfully"}

@router.get("/collections/recent", response_model=List[schemas.CollectionResponse])
def get_recent_collections(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get recent collections across all collectors"""
    collections = db.query(models.Collection).order_by(
        models.Collection.collected_at.desc()
    ).limit(limit).all()
    
    result = []
    for col in collections:
        item = db.query(models.RecyclableItem).filter(
            models.RecyclableItem.id == col.item_id
        ).first()
        
        result.append({
            "id": col.id,
            "collector_id": col.collector_id,
            "item_id": col.item_id,
            "weight_kg": col.weight_kg,
            "earned_amount": col.earned_amount,
            "location": col.location,
            "notes": col.notes,
            "collected_at": col.collected_at,
            "item_name": item.name if item else None,
            "item_category": item.category if item else None
        })
    
    return result