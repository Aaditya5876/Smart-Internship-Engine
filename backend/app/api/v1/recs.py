# backend/app/api/v1/recs.py

from typing import List

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.schemas import RecommendIn, RecommendationResponse, RecItem
from app.models.models import Student, Job, Recommendation, User
from app.services.deps import get_db, get_current_user
from app.ml.features import build_pair_features, get_input_dim
from app.ml.model import load_global_model

router = APIRouter(prefix="/recs", tags=["recs"])


def _require_torch():
    """
    Standard backend pattern:
    - Keep API server runnable without ML deps
    - Only require torch when /recs endpoint is called
    """
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Recommendation service is not enabled because ML dependencies are missing. "
                "Install with: pip install -r requirements-ml.txt"
            ),
        )


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(
    payload: RecommendIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recommend internships/jobs using the current ML model.

    - STUDENT can only request for themselves.
    - ADMIN can request for any student.
    """

    # Role guard
    if current_user.role not in ("student", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Only students or admins can request recommendations",
        )

    # Ensure ML deps exist before any torch usage
    _require_torch()
    import torch  # local import after check (keeps server start clean)

    # Fetch student
    student = db.query(Student).filter(Student.student_uid == payload.student_uid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Student can only request their own recommendations
    if current_user.role == "student" and student.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to get recommendations for this student",
        )

    # Fetch active jobs
    jobs: List[Job] = db.query(Job).filter(Job.is_active == True).all()  # noqa: E712
    if not jobs:
        raise HTTPException(status_code=404, detail="No active jobs found")

    # Load model
    input_dim = get_input_dim()
    model = load_global_model(input_dim)
    model.eval()

    # Build features for each (student, job) pair
    X_list = []
    job_refs: List[Job] = []

    for job in jobs:
        x = build_pair_features(student, job)
        X_list.append(x)
        job_refs.append(job)

    X = np.stack(X_list).astype(np.float32)
    X_tensor = torch.from_numpy(X)

    # Predict scores
    with torch.no_grad():
        scores = model(X_tensor).squeeze().cpu().numpy()

    # Rank and select top K
    ranked = sorted(zip(job_refs, scores), key=lambda x: x[1], reverse=True)
    top = ranked[: payload.top_k]

    # Persist + return response
    rec_items: List[RecItem] = []
    for job, score in top:
        db.add(Recommendation(student_id=student.id, job_id=job.id, score=float(score)))

        rec_items.append(
            RecItem(
                job_uid=job.job_uid,
                role=job.role,
                company=job.company,
                score=float(score),
                required_skills=job.required_skills or "",
                salary_min=job.salary_min,
                salary_max=job.salary_max,
            )
        )

    db.commit()
    return RecommendationResponse(student_uid=student.student_uid, items=rec_items)
