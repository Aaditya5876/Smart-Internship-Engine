# app/api/v1/recs.py
from typing import List

import numpy as np
import torch
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.schemas import RecommendIn, RecommendationResponse, RecItem
from app.models.models import Student, Job, Recommendation, User
from app.services.deps import get_db, get_current_user
from app.ml.features import build_skill_vocab, build_feature_vector
from app.ml.model import load_global_model

router = APIRouter(prefix="/recs", tags=["recs"])


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(
    payload: RecommendIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get job recommendations for a student using the trained PFL global model.

    - STUDENT can only request for themselves.
    - ADMIN can request for any student.
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

    # Build vocab and infer input dimension (must match training)
    vocab = build_skill_vocab(db)
    input_dim = (len(vocab) + 2) + (len(vocab) + 3)

    # Load global PFL model
    model = load_global_model(input_dim)
    model.eval()

    # Build feature matrix
    X_list = []
    job_refs = []
    for job in jobs:
        x = build_feature_vector(student, job, vocab)
        X_list.append(x)
        job_refs.append(job)

    X = np.stack(X_list).astype(np.float32)
    X_tensor = torch.from_numpy(X)

    with torch.no_grad():
        scores = model(X_tensor).squeeze().numpy()

    # Rank jobs by score
    ranked = sorted(zip(job_refs, scores), key=lambda x: x[1], reverse=True)
    top = ranked[: payload.top_k]

    rec_items: List[RecItem] = []
    for job, score in top:
        rec = Recommendation(student_id=student.id, job_id=job.id, score=float(score))
        db.add(rec)

        rec_items.append(
            RecItem(
                job_uid=job.job_uid,
                role=job.role,
                company=job.company,
                score=float(score),
                required_skills=(job.required_skills or ""),
                salary_min=job.salary_min,
                salary_max=job.salary_max,
            )
        )

    db.commit()
    return RecommendationResponse(student_uid=student.student_uid, items=rec_items)
