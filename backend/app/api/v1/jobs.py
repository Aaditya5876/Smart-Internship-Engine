from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.schemas import JobCreate, JobOut, JobUpdate
from app.models.models import Job, User
from app.services.deps import get_db, get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _ensure_employer_or_admin(user: User):
    if user.role not in ("employer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers or admins can manage jobs",
        )


@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_employer_or_admin(current_user)

    existing = db.query(Job).filter(Job.job_uid == payload.job_uid).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="job_uid already exists",
        )

    job = Job(
        job_uid=payload.job_uid,
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


@router.get("/", response_model=List[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    """
    Public: list all active jobs.
    """
    return db.query(Job).filter(Job.is_active == True).all()  # noqa: E712


@router.get("/{job_uid}", response_model=JobOut)
def get_job(job_uid: str, db: Session = Depends(get_db)):
    """
    Public: get a single job.
    """
    job = db.query(Job).filter(Job.job_uid == job_uid).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.put("/{job_uid}", response_model=JobOut)
def update_job(
    job_uid: str,
    payload: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_employer_or_admin(current_user)

    job = db.query(Job).filter(Job.job_uid == job_uid).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if payload.role is not None:
        job.role = payload.role
    if payload.company is not None:
        job.company = payload.company
    if payload.location is not None:
        job.location = payload.location
    if payload.required_skills is not None:
        job.required_skills = payload.required_skills
    if payload.description is not None:
        job.description = payload.description
    if payload.salary_min is not None:
        job.salary_min = payload.salary_min
    if payload.salary_max is not None:
        job.salary_max = payload.salary_max
    if payload.is_active is not None:
        job.is_active = payload.is_active

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_employer_or_admin(current_user)

    job = db.query(Job).filter(Job.job_uid == job_uid).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    db.delete(job)
    db.commit()
    return None
