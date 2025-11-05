
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.schemas import FeedbackIn
from app.models.models import Feedback, Student, Job, Recommendation
from app.services.deps import get_db, get_current_user

router = APIRouter()

@router.post("/submit")
def submit_feedback(data: FeedbackIn, db: Session = Depends(get_db), user = Depends(get_current_user)):
    st = db.query(Student).filter(Student.student_uid==data.student_uid).first()
    jb = db.query(Job).filter(Job.job_uid==data.job_uid).first()
    if not st or not jb:
        raise HTTPException(status_code=404, detail="Student or Job not found")
    rec = db.query(Recommendation).filter(Recommendation.student_id==st.id, Recommendation.job_id==jb.id).first()

    fb = Feedback(recommendation_id=rec.id if rec else None, student_id=st.id, job_id=jb.id, liked=data.liked, notes=data.notes)
    db.add(fb); db.commit()
    return {"ok": True}
