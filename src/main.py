from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src import crud, models, schemas
from src.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/blue-plan-items/", response_model=schemas.BluePlanItem)
def create_blue_plan_item(
    blue_plan_item: schemas.BluePlanItemCreate, db: Session = Depends(get_db)
):
    return crud.create_blue_plan_item(db=db, blue_plan_item=blue_plan_item)


@app.get("/blue-plan-items/", response_model=List[schemas.BluePlanItem])
def read_blue_plan_items(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    items = crud.get_blue_plan_items(db, skip=skip, limit=limit)
    return items


@app.get("/blue-plan-items/{item_id}", response_model=schemas.BluePlanItem)
def read_blue_plan_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_blue_plan_item(db, blue_plan_item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Blue Plan Item not found")
    return db_item


@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db=db, project=project)


@app.post("/projects/{project_id}/orange-plan-items/", response_model=schemas.OrangePlanItem)
def create_orange_plan_item_for_project(
    project_id: int, orange_plan_item: schemas.OrangePlanItemCreate, db: Session = Depends(get_db)
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.create_orange_plan_item(db=db, orange_plan_item=orange_plan_item, project_id=project_id)


@app.post("/orange-plan-items/{orange_plan_item_id}/milestones/", response_model=schemas.Milestone)
def create_milestone_for_orange_plan_item(
    orange_plan_item_id: int, milestone: schemas.MilestoneCreate, db: Session = Depends(get_db)
):
    db_orange_plan_item = crud.get_orange_plan_item(db, orange_plan_item_id=orange_plan_item_id)
    if db_orange_plan_item is None:
        raise HTTPException(status_code=404, detail="Orange Plan Item not found")
    return crud.create_milestone(db=db, milestone=milestone, orange_plan_item_id=orange_plan_item_id)


@app.post("/mappings/blue/{blue_plan_item_id}/orange/{orange_plan_item_id}", response_model=schemas.BluePlanItem)
def link_blue_and_orange_items(
    blue_plan_item_id: int, orange_plan_item_id: int, db: Session = Depends(get_db)
):
    updated_blue_item = crud.link_blue_orange_items(
        db=db, blue_plan_item_id=blue_plan_item_id, orange_plan_item_id=orange_plan_item_id
    )
    if updated_blue_item is None:
        raise HTTPException(status_code=404, detail="Blue or Orange Plan Item not found")
    return updated_blue_item


@app.get("/gap-analysis/", response_model=List[schemas.BluePlanItem])
def get_gap_analysis(db: Session = Depends(get_db)):
    return crud.get_gap_analysis(db=db)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Blue-Orange Plan API"}

@app.get("/coverage/unmet", response_model=List[schemas.BluePlanItem])
def read_unmet_requirements(db: Session = Depends(get_db)):
    return crud.get_unmet_requirements(db)
