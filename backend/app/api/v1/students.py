
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schemas import StudentIn, StudentOut
from app.models.models import Student
from app.services.deps import get_db, require_role

router = APIRouter()

@router.get("/", response_model=List[StudentOut])
def list_students(db: Session = Depends(get_db), user = Depends(require_role("admin","uni"))):
    return db.query(Student).all()

@router.post("/", response_model=StudentOut)
def create_student(data: StudentIn, db: Session = Depends(get_db), user = Depends(require_role("admin","uni"))):
    st = Student(**data.model_dump())
    db.add(st); db.commit(); db.refresh(st)
    return st
