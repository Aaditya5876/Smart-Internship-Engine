# app/api/v1/jobs.py

from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.schemas import JobCreate, JobOut, JobUpdate
from app.models.models import Job, User
from app.services.deps import get_db, get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


# ---------- Helpers ----------

def require_employer_or_admin(user: User):
    if user.role not in ("employer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers or admins can manage jobs",
        )


def generate_job_uid() -> str:
    return f"job_{uuid4().hex[:12]}"


# ---------- Create Job ----------

@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_employer_or_admin(current_user)

    job = Job(
        job_uid=generate_job_uid(),
        role=payload.role,
        company=payload.company,
        location=payload.location,
        required_skills=payload.required_skills,
        description=payload.description,
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        is_active=payload.is_active,
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# ---------- Read Jobs ----------

@router.get("/", response_model=List[JobOut])
def list_active_jobs(db: Session = Depends(get_db)):
    """
    Public endpoint.
    Lists all active jobs.
    """
    return db.query(Job).filter(Job.is_active == True).all()  # noqa: E712


@router.get("/{job_uid}", response_model=JobOut)
def get_job(job_uid: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_uid == job_uid).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


# ---------- Update Job ----------

@router.put("/{job_uid}", response_model=JobOut)
def update_job(
    job_uid: str,
    payload: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_employer_or_admin(current_user)

    job = db.query(Job).filter(Job.job_uid == job_uid).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


# ---------- Delete Job ----------

@router.delete("/{job_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_employer_or_admin(current_user)

    job = db.query(Job).filter(Job.job_uid == job_uid).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    db.delete(job)
    db.commit()
    return None
