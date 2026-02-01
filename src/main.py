from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas
from .database import SessionLocal, engine

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


@app.get("/")
def read_root():
    return {"message": "Welcome to the Blue-Orange Plan API"}
