from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/", response_model=list[schemas.Trade])
def list_trades(db: Session = Depends(get_db)):
    return db.query(models.Trade).all()

@router.post("/", response_model=schemas.Trade)
def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    db_trade = models.Trade(**trade.dict())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade
