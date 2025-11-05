
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schemas import JobIn, JobOut
from app.models.models import Job
from app.services.deps import get_db, require_role

router = APIRouter()

@router.get("/", response_model=List[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@router.post("/", response_model=JobOut)
def create_job(data: JobIn, db: Session = Depends(get_db), user = Depends(require_role("admin","company"))):
    jb = Job(**data.model_dump())
    db.add(jb); db.commit(); db.refresh(jb)
    return jb
