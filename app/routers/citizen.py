from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/citizen",
    tags=["Citizen"]
)

@router.get("/items", response_model=List[schemas.RecyclableItemResponse])
def search_recyclable_items(
    query: Optional[str] = Query(None, description="Search query for item name or category"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search recyclable items by name or category.
    Citizens use this to find out if/how to recycle items.
    """
    items_query = db.query(models.RecyclableItem)
    
    # Apply filters
    if query:
        search_filter = or_(
            models.RecyclableItem.name.ilike(f"%{query}%"),
            models.RecyclableItem.category.ilike(f"%{query}%"),
            models.RecyclableItem.instructions.ilike(f"%{query}%")
        )
        items_query = items_query.filter(search_filter)
        
        # Log the query
        citizen_query = models.CitizenQuery(
            query_text=query,
            result_count=items_query.count()
        )
        db.add(citizen_query)
        db.commit()
    
    if category:
        items_query = items_query.filter(models.RecyclableItem.category == category)
    
    items = items_query.offset(skip).limit(limit).all()
    return items

@router.get("/items/{item_id}", response_model=schemas.RecyclableItemResponse)
def get_recyclable_item(item_id: int, db: Session = Depends(get_db)):
    """Get details of a specific recyclable item"""
    item = db.query(models.RecyclableItem).filter(
        models.RecyclableItem.id == item_id
    ).first()
    
    if not item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all available categories"""
    categories = db.query(models.RecyclableItem.category).distinct().all()
    return {"categories": [cat[0] for cat in categories]}

@router.get("/instructions/{item_name}")
def get_recycling_instructions(item_name: str, db: Session = Depends(get_db)):
    """Get recycling instructions for a specific item by name"""
    item = db.query(models.RecyclableItem).filter(
        models.RecyclableItem.name.ilike(f"%{item_name}%")
    ).first()
    
    if not item:
        # Try to find similar items
        similar_items = db.query(models.RecyclableItem).filter(
            or_(
                models.RecyclableItem.name.ilike(f"%{item_name}%"),
                models.RecyclableItem.category.ilike(f"%{item_name}%")
            )
        ).limit(5).all()
        
        if not similar_items:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"No recycling information found for '{item_name}'"
            )
        
        return {
            "message": f"No exact match found for '{item_name}'",
            "similar_items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "category": item.category,
                    "instructions": item.instructions
                }
                for item in similar_items
            ]
        }
    
    return {
        "item_name": item.name,
        "category": item.category,
        "instructions": item.instructions,
        "price_per_kg": item.price_per_kg
    }