from sqlalchemy.orm import Session
from src import models, schemas

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

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def create_orange_plan_item(db: Session, orange_plan_item: schemas.OrangePlanItemCreate, project_id: int):
    db_orange_plan_item = models.OrangePlanItem(**orange_plan_item.model_dump(), project_id=project_id)
    db.add(db_orange_plan_item)
    db.commit()
    db.refresh(db_orange_plan_item)
    return db_orange_plan_item

def get_orange_plan_item(db: Session, orange_plan_item_id: int):
    return db.query(models.OrangePlanItem).filter(models.OrangePlanItem.id == orange_plan_item_id).first()

def create_milestone(db: Session, milestone: schemas.MilestoneCreate, orange_plan_item_id: int):
    db_milestone = models.Milestone(**milestone.model_dump(), orange_plan_item_id=orange_plan_item_id)
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone

def link_blue_orange_items(db: Session, blue_plan_item_id: int, orange_plan_item_id: int):
    db_blue_plan_item = get_blue_plan_item(db, blue_plan_item_id)
    db_orange_plan_item = get_orange_plan_item(db, orange_plan_item_id)

    if db_blue_plan_item and db_orange_plan_item:
        db_blue_plan_item.orange_plan_items.append(db_orange_plan_item)
        db.commit()
        db.refresh(db_blue_plan_item)
        return db_blue_plan_item
    return None

def get_gap_analysis(db: Session):
    return (
        db.query(models.BluePlanItem)
        .join(models.blue_orange_link)
        .join(models.OrangePlanItem)
        .filter(models.BluePlanItem.need_date < models.OrangePlanItem.end_date)
        .all()
    )
