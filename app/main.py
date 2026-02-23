from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import models, database
from pydantic import BaseModel

app = FastAPI(title="Personal Task Manager")

# Create tables on startup
models.Base.metadata.create_all(bind=database.engine)

# Mount frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# --- Pydantic Schemas ---

class TagBase(BaseModel):
    name: str
    color: str = "#6366f1"

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: str = "medium"  # low, medium, high
    tag_ids: List[int] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None
    tag_ids: Optional[List[int]] = None

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[date]
    priority: str
    completed: bool
    tags: List[Tag] = []
    class Config:
        from_attributes = True


# --- Dependency ---

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Routes ---

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

# Tags
@app.get("/api/tags", response_model=List[Tag])
def get_tags(db: Session = Depends(get_db)):
    return db.query(models.Tag).all()

@app.post("/api/tags", response_model=Tag, status_code=201)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    db_tag = models.Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.delete("/api/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()

# Tasks
@app.get("/api/tasks", response_model=List[Task])
def get_tasks(
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    tag_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.Task)
    if completed is not None:
        q = q.filter(models.Task.completed == completed)
    if priority:
        q = q.filter(models.Task.priority == priority)
    if tag_id:
        q = q.filter(models.Task.tags.any(models.Tag.id == tag_id))
    return q.order_by(models.Task.due_date.asc().nullslast(), models.Task.id.desc()).all()

@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    tags = db.query(models.Tag).filter(models.Tag.id.in_(task.tag_ids)).all()
    db_task = models.Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
        tags=tags
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.patch("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updates: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    data = updates.model_dump(exclude_unset=True)
    if "tag_ids" in data:
        task.tags = db.query(models.Tag).filter(models.Tag.id.in_(data.pop("tag_ids"))).all()
    for k, v in data.items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task

@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()

@app.get("/api/health")
def health():
    return {"status": "ok"}