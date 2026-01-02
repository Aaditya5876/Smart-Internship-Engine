from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.schemas import InteractionIn, InteractionOut
from app.models.models import Interaction, Student, Job, User
from app.services.deps import get_db, get_current_user

router = APIRouter(prefix="/interactions", tags=["interactions"])

ALLOWED_EVENTS = {"view", "click", "save", "apply"}


@router.post("/", response_model=InteractionOut, status_code=status.HTTP_201_CREATED)
def log_interaction(
    payload: InteractionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an interaction event.

    - Students may only log interactions for their own profile.
    - Admins may log interactions for any student (useful for testing/backfilling).
    """

    if payload.event_type not in ALLOWED_EVENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event_type. Allowed: {sorted(ALLOWED_EVENTS)}",
        )

    student = db.query(Student).filter(Student.student_uid == payload.student_uid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role != "admin" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to log for this student")

    job = db.query(Job).filter(Job.job_uid == payload.job_uid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    row = Interaction(
        student_id=student.id,
        job_id=job.id,
        event_type=payload.event_type,
        client_id=current_user.client_id,
        meta=payload.meta,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/me", response_model=List[InteractionOut])
def list_my_interactions(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent interactions for the current logged-in student."""

    if current_user.role != "student":
        return []

    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    q = (
        db.query(Interaction)
        .filter(Interaction.student_id == student.id)
        .order_by(Interaction.timestamp.desc())
        .limit(max(1, min(limit, 500)))
    )
    return q.all()
