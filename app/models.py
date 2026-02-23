from sqlalchemy import Column, Integer, String, Boolean, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# Association table for Task <-> Tag many-to-many
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#6366f1")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    due_date = Column(Date, nullable=True)
    priority = Column(String(10), default="medium")  # low | medium | high
    completed = Column(Boolean, default=False)
    tags = relationship("Tag", secondary=task_tags, lazy="joined")
