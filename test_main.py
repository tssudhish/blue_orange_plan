from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.main import app, get_db

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the test database
Base.metadata.create_all(bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Blue-Orange Plan API"}

def test_create_blue_plan_item():
    response = client.post(
        "/blue-plan-items/",
        json={
            "name": "Requirement A",
            "description": "Must handle high traffic",
            "owners": ["Team Alpha"],
            "need_date": "2026-12-31",
            "priority": "High",
            "category": "Performance"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Requirement A"
    assert "id" in data
    assert data["owners"] == ["Team Alpha"]

def test_create_project():
    response = client.post(
        "/projects/",
        json={"name": "Project X", "description": "A new project", "owner": "Team Beta"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Project X"
    assert data["description"] == "A new project"
    assert data["owner"] == "Team Beta"
    assert "id" in data

def test_create_orange_plan_item_for_project():
    # First, create a project
    project_response = client.post(
        "/projects/",
        json={"name": "Project Y", "description": "Another project", "owner": "Team Gamma"},
    )
    assert project_response.status_code == 200
    project_data = project_response.json()
    project_id = project_data["id"]

    # Now, create an orange plan item for that project
    orange_item_response = client.post(
        f"/projects/{project_id}/orange-plan-items/",
        json={
            "name": "Milestone 1",
            "description": "First milestone",
            "start_date": "2026-01-01",
            "end_date": "2026-03-31",
        },
    )
    assert orange_item_response.status_code == 200
    orange_item_data = orange_item_response.json()
    assert orange_item_data["name"] == "Milestone 1"
    assert orange_item_data["description"] == "First milestone"
    assert orange_item_data["project_id"] == project_id
    assert "id" in orange_item_data

def test_create_milestone_for_orange_plan_item():
    # First, create a project
    project_response = client.post(
        "/projects/",
        json={"name": "Project Z", "description": "A third project", "owner": "Team Delta"},
    )
    assert project_response.status_code == 200
    project_data = project_response.json()
    project_id = project_data["id"]

    # Then, create an orange plan item for that project
    orange_item_response = client.post(
        f"/projects/{project_id}/orange-plan-items/",
        json={
            "name": "Release 1",
            "description": "First release",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
        },
    )
    assert orange_item_response.status_code == 200
    orange_item_data = orange_item_response.json()
    orange_item_id = orange_item_data["id"]

    # Now, create a milestone for that orange plan item
    milestone_response = client.post(
        f"/orange-plan-items/{orange_item_id}/milestones/",
        json={
            "name": "Q1 Milestone",
            "description": "End of Q1",
            "date": "2026-03-31",
            "status": "Planned",
        },
    )
    assert milestone_response.status_code == 200
    milestone_data = milestone_response.json()
    assert milestone_data["name"] == "Q1 Milestone"
    assert milestone_data["description"] == "End of Q1"
    assert milestone_data["orange_plan_item_id"] == orange_item_id
    assert "id" in milestone_data

def test_link_blue_and_orange_items():
    # Create a blue plan item
    blue_item_response = client.post(
        "/blue-plan-items/",
        json={
            "name": "Requirement B",
            "description": "A new requirement",
            "owners": ["Team Epsilon"],
            "need_date": "2027-01-01",
            "priority": "Medium",
            "category": "UI",
        },
    )
    assert blue_item_response.status_code == 200
    blue_item_data = blue_item_response.json()
    blue_item_id = blue_item_data["id"]

    # Create a project and an orange plan item
    project_response = client.post(
        "/projects/",
        json={"name": "Project Omega", "description": "A final project", "owner": "Team Omega"},
    )
    assert project_response.status_code == 200
    project_data = project_response.json()
    project_id = project_data["id"]

    orange_item_response = client.post(
        f"/projects/{project_id}/orange-plan-items/",
        json={
            "name": "Feature X",
            "description": "A new feature",
            "start_date": "2026-08-01",
            "end_date": "2026-11-30",
        },
    )
    assert orange_item_response.status_code == 200
    orange_item_data = orange_item_response.json()
    orange_item_id = orange_item_data["id"]

    # Link the two items
    link_response = client.post(
        f"/mappings/blue/{blue_item_id}/orange/{orange_item_id}"
    )
    assert link_response.status_code == 200
    updated_blue_item_data = link_response.json()
    
    assert updated_blue_item_data["id"] == blue_item_id
    assert len(updated_blue_item_data["orange_plan_items"]) == 1
    assert updated_blue_item_data["orange_plan_items"][0]["id"] == orange_item_id
    assert updated_blue_item_data["orange_plan_items"][0]["name"] == "Feature X"

def test_get_gap_analysis():
    # Create a blue plan item with a need_date that has a gap
    gap_blue_item_response = client.post(
        "/blue-plan-items/",
        json={
            "name": "Gap Requirement",
            "description": "This one has a gap",
            "owners": ["Team Gap"],
            "need_date": "2026-06-01",
            "priority": "High",
            "category": "Backend",
        },
    )
    assert gap_blue_item_response.status_code == 200
    gap_blue_item_data = gap_blue_item_response.json()
    gap_blue_item_id = gap_blue_item_data["id"]

    # Create a blue plan item with a need_date that does not have a gap
    no_gap_blue_item_response = client.post(
        "/blue-plan-items/",
        json={
            "name": "No Gap Requirement",
            "description": "This one is fine",
            "owners": ["Team NoGap"],
            "need_date": "2027-01-01",
            "priority": "Low",
            "category": "Frontend",
        },
    )
    assert no_gap_blue_item_response.status_code == 200
    no_gap_blue_item_data = no_gap_blue_item_response.json()
    no_gap_blue_item_id = no_gap_blue_item_data["id"]

    # Create a project and an orange plan item with an end_date
    project_response = client.post(
        "/projects/",
        json={"name": "Project Alpha", "description": "A test project", "owner": "Team Alpha"},
    )
    assert project_response.status_code == 200
    project_data = project_response.json()
    project_id = project_data["id"]

    orange_item_response = client.post(
        f"/projects/{project_id}/orange-plan-items/",
        json={
            "name": "Release 2026",
            "description": "The only release this year",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        },
    )
    assert orange_item_response.status_code == 200
    orange_item_data = orange_item_response.json()
    orange_item_id = orange_item_data["id"]

    # Link both blue items to the orange item
    client.post(f"/mappings/blue/{gap_blue_item_id}/orange/{orange_item_id}")
    client.post(f"/mappings/blue/{no_gap_blue_item_id}/orange/{orange_item_id}")

    # Get the gap analysis
    gap_analysis_response = client.get("/gap-analysis/")
    assert gap_analysis_response.status_code == 200
    gap_analysis_data = gap_analysis_response.json()

    # Check that only the item with the gap is returned
    assert gap_analysis_data[0]["id"] == gap_blue_item_id
    assert gap_analysis_data[0]["name"] == "Gap Requirement"


def test_create_milestone_for_new_orange_plan_item():
    # Create a project
    project_response = client.post(
        "/projects/",
        json={"name": "Project Milestone", "description": "Project for testing milestones", "owner": "Team Milestone"},
    )
    assert project_response.status_code == 200
    project_data = project_response.json()
    project_id = project_data["id"]

    # Create an orange plan item for that project
    orange_item_response = client.post(
        f"/projects/{project_id}/orange-plan-items/",
        json={
            "name": "Release 2",
            "description": "Second release",
            "start_date": "2027-01-01",
            "end_date": "2027-06-30",
        },
    )
    assert orange_item_response.status_code == 200
    orange_item_data = orange_item_response.json()
    orange_item_id = orange_item_data["id"]

    # Create a milestone for the new orange plan item
    milestone_response = client.post(
        f"/orange-plan-items/{orange_item_id}/milestones/",
        json={
            "name": "Q2 Milestone",
            "description": "End of Q2",
            "date": "2027-06-30",
            "status": "Planned",
        },
    )
    assert milestone_response.status_code == 200
    milestone_data = milestone_response.json()
    assert milestone_data["name"] == "Q2 Milestone"
    assert milestone_data["description"] == "End of Q2"
    assert milestone_data["orange_plan_item_id"] == orange_item_id
    assert "id" in milestone_data

def test_import_requirements_csv():
    csv_content = """name,description,owners,need_date,priority,category
Imported Req 1,Description 1,"Owner A, Owner B",2027-12-01,High,Category A
Imported Req 2,Description 2,Owner C,2027-12-02,Medium,Category B
"""
    files = {'file': ('test_import.csv', csv_content, 'text/csv')}
    
    # We use follow_redirects=False to assert the 303 redirect response specifically
    response = client.post("/dashboard/import-requirements", files=files, follow_redirects=False)
    assert response.status_code == 303
    
    # Verify the items were created by fetching the list
    response = client.get("/blue-plan-items/")
    items = response.json()
    
    imported_item_1 = next((item for item in items if item["name"] == "Imported Req 1"), None)
    assert imported_item_1 is not None
    assert imported_item_1["owners"] == ["Owner A", "Owner B"]
    assert imported_item_1["need_date"] == "2027-12-01"

def test_import_requirements_csv_missing_columns():
    csv_content = """name,description
Incomplete Req,Missing columns
"""
    files = {'file': ('bad_import.csv', csv_content, 'text/csv')}
    
    response = client.post("/dashboard/import-requirements", files=files)
    assert response.status_code == 400
    assert "CSV file missing required columns" in response.json()["detail"]

def test_export_requirements():
    # Create a dummy item first to ensure there is data to export
    client.post(
        "/blue-plan-items/",
        json={
            "name": "Exportable Req",
            "description": "To be exported",
            "owners": ["Team Export"],
            "need_date": "2027-12-31",
            "priority": "Low",
            "category": "Export"
        },
    )
    
    response = client.get("/dashboard/export-requirements")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    content = response.text
    assert "name,description,owners,need_date,priority,category" in content
    assert "Exportable Req" in content
    assert "Team Export" in content
