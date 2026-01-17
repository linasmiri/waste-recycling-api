from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from .. import models, schemas
from ..database import get_db
from ..auth import (
    get_password_hash, 
    authenticate_collector, 
    create_access_token,
    get_current_collector
)

router = APIRouter(
    prefix="/collectors",
    tags=["Collectors"]
)

@router.post("/register", response_model=schemas.CollectorResponse, status_code=status.HTTP_201_CREATED)
def register_collector(collector: schemas.CollectorCreate, db: Session = Depends(get_db)):
    """Register a new collector (Barbecha)"""
    # Check if username exists
    db_collector = db.query(models.Collector).filter(
        models.Collector.username == collector.username
    ).first()
    
    if db_collector:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new collector
    hashed_password = get_password_hash(collector.password)
    new_collector = models.Collector(
        username=collector.username,
        full_name=collector.full_name,
        phone_number=collector.phone_number,
        hashed_password=hashed_password
    )
    
    db.add(new_collector)
    db.commit()
    db.refresh(new_collector)
    
    return new_collector

@router.post("/login")
def login_collector(credentials: schemas.CollectorLogin, db: Session = Depends(get_db)):
    """Login collector and return JWT token"""
    collector = authenticate_collector(db, credentials.username, credentials.password)
    
    if not collector:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": collector.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "collector": {
            "id": collector.id,
            "username": collector.username,
            "full_name": collector.full_name,
            "balance": collector.balance
        }
    }

@router.get("/me", response_model=schemas.CollectorResponse)
def get_current_collector_info(current_collector: models.Collector = Depends(get_current_collector)):
    """Get current collector information"""
    return current_collector

@router.get("/me/stats", response_model=schemas.CollectorStats)
def get_collector_stats(
    current_collector: models.Collector = Depends(get_current_collector),
    db: Session = Depends(get_db)
):
    """Get collector statistics"""
    # Total collections
    total_collections = db.query(models.Collection).filter(
        models.Collection.collector_id == current_collector.id
    ).count()
    
    # Total weight and earnings
    stats = db.query(
        func.sum(models.Collection.weight_kg).label("total_weight"),
        func.sum(models.Collection.earned_amount).label("total_earned")
    ).filter(
        models.Collection.collector_id == current_collector.id
    ).first()
    
    # Collections by category
    category_stats = db.query(
        models.RecyclableItem.category,
        func.count(models.Collection.id).label("count"),
        func.sum(models.Collection.weight_kg).label("weight")
    ).join(
        models.Collection, models.Collection.item_id == models.RecyclableItem.id
    ).filter(
        models.Collection.collector_id == current_collector.id
    ).group_by(
        models.RecyclableItem.category
    ).all()
    
    collections_by_category = {
        cat.category: {
            "count": cat.count,
            "weight_kg": float(cat.weight or 0)
        }
        for cat in category_stats
    }
    
    return {
        "total_collections": total_collections,
        "total_weight_kg": float(stats.total_weight or 0),
        "total_earned": float(stats.total_earned or 0),
        "balance": current_collector.balance,
        "collections_by_category": collections_by_category
    }

@router.post("/collections", response_model=schemas.CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    collection: schemas.CollectionCreate,
    current_collector: models.Collector = Depends(get_current_collector),
    db: Session = Depends(get_db)
):
    """Record a new collection"""
    # Verify item exists
    item = db.query(models.RecyclableItem).filter(
        models.RecyclableItem.id == collection.item_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Recyclable item not found")
    
    # Calculate earnings
    earned_amount = collection.weight_kg * item.price_per_kg
    
    # Create collection record
    new_collection = models.Collection(
        collector_id=current_collector.id,
        item_id=collection.item_id,
        weight_kg=collection.weight_kg,
        earned_amount=earned_amount,
        location=collection.location,
        notes=collection.notes
    )
    
    # Update collector stats
    current_collector.balance += earned_amount
    current_collector.total_collected_kg += collection.weight_kg
    
    # Create transaction record
    transaction = models.Transaction(
        collector_id=current_collector.id,
        transaction_type="collection",
        amount=earned_amount,
        description=f"Collected {collection.weight_kg}kg of {item.name}"
    )
    
    db.add(new_collection)
    db.add(transaction)
    db.commit()
    db.refresh(new_collection)
    
    return {
        **collection.dict(),
        "id": new_collection.id,
        "collector_id": current_collector.id,
        "earned_amount": earned_amount,
        "collected_at": new_collection.collected_at,
        "item_name": item.name,
        "item_category": item.category
    }

@router.get("/collections", response_model=List[schemas.CollectionResponse])
def get_my_collections(
    skip: int = 0,
    limit: int = 50,
    current_collector: models.Collector = Depends(get_current_collector),
    db: Session = Depends(get_db)
):
    """Get collector's collection history"""
    collections = db.query(models.Collection).filter(
        models.Collection.collector_id == current_collector.id
    ).order_by(
        models.Collection.collected_at.desc()
    ).offset(skip).limit(limit).all()
    
    # Add item details
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

@router.post("/withdraw", response_model=schemas.TransactionResponse)
def withdraw_balance(
    withdrawal: schemas.TransactionCreate,
    current_collector: models.Collector = Depends(get_current_collector),
    db: Session = Depends(get_db)
):
    """Withdraw balance"""
    if withdrawal.amount > current_collector.balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Update balance
    current_collector.balance -= withdrawal.amount
    
    # Create transaction
    transaction = models.Transaction(
        collector_id=current_collector.id,
        transaction_type="withdrawal",
        amount=-withdrawal.amount,
        description=withdrawal.description or "Balance withdrawal"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction

@router.get("/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 50,
    current_collector: models.Collector = Depends(get_current_collector),
    db: Session = Depends(get_db)
):
    """Get transaction history"""
    transactions = db.query(models.Transaction).filter(
        models.Transaction.collector_id == current_collector.id
    ).order_by(
        models.Transaction.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return transactions