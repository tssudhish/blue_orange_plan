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
            "need_date": "2024-12-31",
            "priority": "High",
            "category": "Performance"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Requirement A"
    assert "id" in data
    assert data["owners"] == ["Team Alpha"]
