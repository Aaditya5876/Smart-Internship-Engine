from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.schemas import RecommendIn, RecommendationResponse, RecItem
from app.models.models import Student, Job, Recommendation, User
from app.services.deps import get_db, get_current_user

router = APIRouter(prefix="/recs", tags=["recs"])


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(
    payload: RecommendIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get job recommendations for a student.

    - STUDENT can only request for their own student_uid.
    - ADMIN can request for any student_uid.
    """
    if current_user.role not in ("student", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Only students or admins can request recommendations",
        )

    student = db.query(Student).filter(Student.student_uid == payload.student_uid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role == "student" and student.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to get recommendations for this student",
        )

    jobs: List[Job] = db.query(Job).filter(Job.is_active == True).all()  # noqa: E712
    if not jobs:
        raise HTTPException(status_code=404, detail="No active jobs found")

    # Dummy scoring for now – will be replaced by PFL
    scored = []
    base_score = 1.0
    step = 0.01
    for idx, job in enumerate(jobs):
        score = max(base_score - idx * step, 0.0)
        scored.append((job, float(score)))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[: payload.top_k]

    rec_items: List[RecItem] = []
    for job, score in top:
        rec = Recommendation(student_id=student.id, job_id=job.id, score=score)
        db.add(rec)

        rec_items.append(
            RecItem(
                job_uid=job.job_uid,
                role=job.role,
                company=job.company,
                score=score,
                required_skills=(job.required_skills or ""),
                salary_min=job.salary_min,
                salary_max=job.salary_max,
            )
        )

    db.commit()
    return RecommendationResponse(student_uid=student.student_uid, items=rec_items)
