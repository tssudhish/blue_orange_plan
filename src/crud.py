from sqlalchemy.orm import Session
from . import models, schemas

def get_blue_plan_item(db: Session, blue_plan_item_id: int):
    return db.query(models.BluePlanItem).filter(models.BluePlanItem.id == blue_plan_item_id).first()

def get_blue_plan_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BluePlanItem).offset(skip).limit(limit).all()

def create_blue_plan_item(db: Session, blue_plan_item: schemas.BluePlanItemCreate):
    db_blue_plan_item = models.BluePlanItem(**blue_plan_item.model_dump())
    db.add(db_blue_plan_item)
    db.commit()
    db.refresh(db_blue_plan_item)
    return db_blue_plan_item
