# Blue Orange Plan - Software Architecture

## 1. Introduction
The Blue Orange Plan application is a program management tool designed to align high-level requirements ("Blue Plan") with project execution milestones ("Orange Plan"). It facilitates the identification of gaps between requirement need dates and project delivery dates within a large organization.

## 2. System Overview
The system follows a standard **RESTful API** architecture using a layered approach. It separates concerns into API routing, data validation (schemas), database operations (CRUD), and data modeling.

### High-Level Components
1.  **Client**: (Future) Web Portal / Frontend to visualize the plans.
2.  **API Layer**: FastAPI application handling HTTP requests and responses.
3.  **Service/Data Layer**: Logic to manipulate data and interact with the database.
4.  **Database**: Relational database storing plans, projects, and mappings.

## 3. Technology Stack
*   **Language**: Python
*   **Web Framework**: FastAPI
    *   Selected for high performance, automatic interactive documentation (Swagger UI), and native support for asynchronous operations.
*   **ORM (Object-Relational Mapping)**: SQLAlchemy
    *   Used to interact with the database using Python classes instead of raw SQL, facilitating the management of relationships between Blue and Orange plans.
*   **Data Validation**: Pydantic (via FastAPI schemas)
    *   Ensures that incoming data for Blue and Orange plans meets the required formats before processing.
*   **Database**: SQLite (for development).

## 4. Application Structure
The source code is organized into modular components:

*   **`run.py`**: The entry point of the application, responsible for running the Uvicorn server.
*   **`src/main.py`**: The entry point of the application. It initializes the FastAPI app, configures dependency injection for database sessions (`get_db`), and defines the API routes.
*   **`src/models.py`**: Defines the database schema using SQLAlchemy classes. This represents the "Truth" of the data structure (e.g., `BluePlanItem` table).
*   **`src/schemas.py`**: Defines Pydantic models used for request parsing (e.g., `BluePlanItemCreate`) and response formatting.
*   **`src/crud.py`**: Contains the Create, Read, Update, Delete functions. This isolates database logic from the API routes.
*   **`src/database.py`**: Handles database connection configuration (`SessionLocal`, `engine`).
*   **`test_main.py`**: Contains the tests for the application, using `pytest` and an in-memory SQLite database.

## 5. Data Model (Conceptual)
Based on the business logic described in the README and current code:

### Entities
1.  **Blue Plan Item** (Implemented)
    *   Represents a stakeholder requirement.
    *   **Attributes**: ID, Description, Owner, Need Date.
    *   **Constraints**: Generally immutable.
2.  **Project** (Implemented)
    *   Represents a team or domain executing work within the program.
3.  **Orange Plan Item** (Implemented)
    *   Represents a project milestone or "Business Release" (BR).
    *   **Attributes**: ID, Project ID, Delivery Date, Capabilities.
4.  **Milestone** (Implemented)
    *   Represents a milestone within an Orange Plan Item.
5.  **Blue-Orange Mapping** (Implemented)
    *   A Many-to-Many association between Blue Plan Items and Orange Plan Items.

### Relationships
*   **Many-to-Many**:
    *   One Blue Plan Item can be satisfied by multiple Orange Plan Items.
    *   One Orange Plan Item can satisfy multiple Blue Plan Items.
*   **One-to-Many**:
    *   One Project can have multiple Orange Plan Items.
    *   One Orange Plan Item can have multiple Milestones.

## 6. API Design
The API follows REST principles.

### Current Endpoints
*   `GET /`: Health check / Welcome message.
*   `POST /blue-plan-items/`: Create a new Blue Plan requirement.
    *   *Input*: JSON body matching `BluePlanItemCreate` schema.
*   `GET /blue-plan-items/`: List requirements.
    *   *Parameters*: `skip` (offset), `limit` (pagination).
*   `GET /blue-plan-items/{item_id}`: Retrieve a specific requirement by ID.

### Future Endpoints (Planned)
*   `POST /orange-plan-items/`: Submit project milestones.
*   `POST /projects/`: Create a new project.
*   `POST /milestones/`: Create a new milestone.
*   `POST /mappings/`: Link a Blue Item to an Orange Item.
*   `GET /gap-analysis/`: A view comparing Blue Plan "Need Dates" vs. Orange Plan "Delivery Dates".

## 7. Business Logic & Validation
The system is designed to handle specific program management logic:

1.  **Gap Analysis**: The system must calculate if an Orange Plan Item's delivery date is later than the linked Blue Plan Item's need date.
2.  **Coverage**: Identify Blue Plan items that have no linked Orange Plan items (unmet requirements).
3.  **Partial Satisfaction**: Handle cases where a project only partially satisfies a requirement.
