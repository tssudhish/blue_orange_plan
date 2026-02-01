from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

class BluePlanItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    owners: List[str] = []
    need_date: date
    priority: str
    category: str
    external_id: Optional[str] = None

class BluePlanItemCreate(BluePlanItemBase):
    pass

class BluePlanItem(BluePlanItemBase):
    id: int
    orange_plan_items: List["OrangePlanItem"] = []

    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    owner: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    orange_plan_items: List["OrangePlanItem"] = []

    model_config = ConfigDict(from_attributes=True)

class OrangePlanItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    external_id: Optional[str] = None

class OrangePlanItemCreate(OrangePlanItemBase):
    pass

class OrangePlanItem(OrangePlanItemBase):
    id: int
    project_id: int
    milestones: List["Milestone"] = []
    blue_plan_items: List[BluePlanItem] = []

    model_config = ConfigDict(from_attributes=True)

class MilestoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    date: date
    status: str

class MilestoneCreate(MilestoneBase):
    pass

class Milestone(MilestoneBase):
    id: int
    orange_plan_item_id: int

    model_config = ConfigDict(from_attributes=True)

# Update forward references
Project.model_rebuild()
BluePlanItem.model_rebuild()
OrangePlanItem.model_rebuild()
