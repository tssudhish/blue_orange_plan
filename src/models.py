from sqlalchemy import Column, Integer, String, Date, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

blue_orange_link = Table(
    "blue_orange_link",
    Base.metadata,
    Column("blue_plan_item_id", Integer, ForeignKey("blue_plan_items.id"), primary_key=True),
    Column("orange_plan_item_id", Integer, ForeignKey("orange_plan_items.id"), primary_key=True),
)


class BluePlanItem(Base):
    __tablename__ = "blue_plan_items"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, index=True)
    description = Column(String)
    owners = Column(JSON)
    need_date = Column(Date)
    priority = Column(String)
    category = Column(String)

    orange_plan_items = relationship(
        "OrangePlanItem", secondary=blue_orange_link, back_populates="blue_plan_items"
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    owner = Column(String)

    orange_plan_items = relationship("OrangePlanItem", back_populates="project")


class OrangePlanItem(Base):
    __tablename__ = "orange_plan_items"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, index=True)
    description = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))
    start_date = Column(Date)
    end_date = Column(Date)

    project = relationship("Project", back_populates="orange_plan_items")
    milestones = relationship("Milestone", back_populates="orange_plan_item")
    blue_plan_items = relationship(
        "BluePlanItem", secondary=blue_orange_link, back_populates="orange_plan_items"
    )


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    date = Column(Date)
    status = Column(String)
    orange_plan_item_id = Column(Integer, ForeignKey("orange_plan_items.id"))

    orange_plan_item = relationship("OrangePlanItem", back_populates="milestones")
