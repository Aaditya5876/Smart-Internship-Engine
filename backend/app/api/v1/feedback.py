from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.schemas import FeedbackIn, FeedbackOut
from app.models.models import Student, Job, Recommendation, Feedback, User
from app.services.deps import get_db, get_current_user

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/submit", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit feedback for a recommendation.

    - STUDENT can only submit for their own student_uid.
    - ADMIN can submit for any.
    """
    if current_user.role not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students or admins can submit feedback",
        )

    student = db.query(Student).filter(Student.student_uid == payload.student_uid).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    if current_user.role == "student" and student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit feedback for this student",
        )

    job = db.query(Job).filter(Job.job_uid == payload.job_uid).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # most recent recommendation for this student-job pair, if any
    recommendation = (
        db.query(Recommendation)
        .filter(Recommendation.student_id == student.id, Recommendation.job_id == job.id)
        .order_by(Recommendation.created_at.desc())
        .first()
    )

    fb = Feedback(
        student_id=student.id,
        job_id=job.id,
        recommendation_id=recommendation.id if recommendation else None,
        liked=payload.liked,
        notes=payload.notes,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
