from fastapi import Depends, FastAPI, HTTPException, Form, UploadFile, File
import csv
import io
import json
from sqlalchemy.orm import Session
from typing import List

from src import crud, models, schemas
from src.database import SessionLocal, engine

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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

# Setup templates and static files
templates = Jinja2Templates(directory="src/templates")
app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/resources", StaticFiles(directory="src/resources"), name="resources")

@app.post("/dashboard/add-requirement")
async def add_requirement_ui(
    name: str = Form(...),
    description: str = Form(...),
    owners: str = Form(...),
    need_date: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db)
):
    owners_list = [o.strip() for o in owners.split(",") if o.strip()]
    item_data = schemas.BluePlanItemCreate(
        name=name,
        description=description,
        owners=owners_list,
        need_date=need_date,
        priority=priority,
        category=category
    )
    crud.create_blue_plan_item(db=db, blue_plan_item=item_data)
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/dashboard/add-project")
async def add_project_ui(
    name: str = Form(...),
    description: str = Form(...),
    owner: str = Form(...),
    db: Session = Depends(get_db)
):
    project_data = schemas.ProjectCreate(
        name=name,
        description=description,
        owner=owner
    )
    crud.create_project(db=db, project=project_data)
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/dashboard/create-test-project")
async def create_test_project_ui(db: Session = Depends(get_db)):
    # Create Project
    project_data = schemas.ProjectCreate(
        name="Blue-Orange Test Project",
        description="Standard test project for validating requirements",
        owner="PMO Team"
    )
    project = crud.create_project(db=db, project=project_data)

    # Create Orange Plan Items (Releases)
    # Release 1: Fits 2024 requirements (End Date: Nov 30, 2024)
    op_item1 = schemas.OrangePlanItemCreate(
        name="Release 1.0 (Q4 2024)",
        description="End of year release",
        start_date="2024-10-01",
        end_date="2024-11-30"
    )
    crud.create_orange_plan_item(db=db, orange_plan_item=op_item1, project_id=project.id)

    # Release 2: Fits early 2025, but might gap late Feb items if delayed (End Date: Mar 15, 2025)
    op_item2 = schemas.OrangePlanItemCreate(
        name="Release 1.1 (Q1 2025)",
        description="Early 2025 release",
        start_date="2025-01-01",
        end_date="2025-03-15"
    )
    crud.create_orange_plan_item(db=db, orange_plan_item=op_item2, project_id=project.id)

    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/dashboard/import-projects/check", response_class=HTMLResponse)
async def check_project_import(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    # Group data by project
    projects_data = {}
    for row in csv_reader:
        p_name = row.get("project_name")
        if not p_name: continue
        
        if p_name not in projects_data:
            projects_data[p_name] = {
                "name": p_name,
                "description": row.get("project_description", ""),
                "owner": row.get("project_owner", ""),
                "releases": []
            }
        
        if row.get("release_name"):
            projects_data[p_name]["releases"].append({
                "name": row.get("release_name"),
                "description": row.get("release_description", ""),
                "start_date": row.get("start_date"),
                "end_date": row.get("end_date")
            })

    # Compare with DB
    changes = []
    for p_name, p_data in projects_data.items():
        existing_project = crud.get_project_by_name(db, p_name)
        status = "Update" if existing_project else "New"
        
        changes.append({
            "status": status,
            "project": p_data,
            "existing_id": existing_project.id if existing_project else None
        })

    return templates.TemplateResponse("project_import_confirm.html", {
        "request": request,
        "changes": changes,
        "json_data": json.dumps(changes)
    })

@app.post("/dashboard/import-projects/confirm")
async def confirm_project_import(
    data: str = Form(...),
    db: Session = Depends(get_db)
):
    changes = json.loads(data)
    
    for item in changes:
        p_data = item["project"]
        project_schema = schemas.ProjectCreate(
            name=p_data["name"], description=p_data["description"], owner=p_data["owner"]
        )
        
        if item["status"] == "New":
            project = crud.create_project(db, project_schema)
        else:
            project = crud.update_project(db, item["existing_id"], project_schema)
            
        for r_data in p_data["releases"]:
            release_schema = schemas.OrangePlanItemCreate(**r_data)
            existing_release = crud.get_orange_plan_item_by_name(db, r_data["name"], project.id)
            if existing_release:
                crud.update_orange_plan_item(db, existing_release.id, release_schema)
            else:
                crud.create_orange_plan_item(db, release_schema, project.id)
                
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/dashboard/import-requirements")
async def import_requirements(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if file.filename.endswith('.csv'):
        content = await file.read()
        # Decode bytes to string
        decoded_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded_content))
        
        required_columns = {"name", "description", "owners", "need_date", "priority", "category"}
        if not csv_reader.fieldnames or not required_columns.issubset(set(csv_reader.fieldnames)):
            missing = required_columns - set(csv_reader.fieldnames or [])
            raise HTTPException(status_code=400, detail=f"CSV file missing required columns: {', '.join(missing)}")

        for row in csv_reader:
            # Parse owners list from comma-separated string in CSV
            owners_raw = row.get("owners", "")
            owners_list = [o.strip() for o in owners_raw.split(",") if o.strip()]
            
            item_data = schemas.BluePlanItemCreate(
                name=row.get("name"),
                description=row.get("description"),
                owners=owners_list,
                need_date=row.get("need_date"), # Expects YYYY-MM-DD
                priority=row.get("priority"),
                category=row.get("category")
            )
            crud.create_blue_plan_item(db=db, blue_plan_item=item_data)
            
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/dashboard/export-requirements")
def export_requirements(db: Session = Depends(get_db)):
    # Fetch all items (using a high limit to ensure we get everything)
    items = crud.get_blue_plan_items(db, limit=10000)
    
    stream = io.StringIO()
    csv_writer = csv.writer(stream)
    
    # Write Header
    csv_writer.writerow(["name", "description", "owners", "need_date", "priority", "category"])
    
    # Write Data
    for item in items:
        owners_str = ", ".join(item.owners) if item.owners else ""
        csv_writer.writerow([
            item.name,
            item.description,
            owners_str,
            item.need_date,
            item.priority,
            item.category
        ])
    
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=requirements_export.csv"
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request, db: Session = Depends(get_db)):
    # Fetch data to display on the portal
    blue_items = crud.get_blue_plan_items(db)
    gap_analysis = crud.get_gap_analysis(db)
    unmet_requirements = crud.get_unmet_requirements(db)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "blue_items": blue_items,
        "gap_analysis": gap_analysis,
        "unmet_requirements": unmet_requirements
    })
