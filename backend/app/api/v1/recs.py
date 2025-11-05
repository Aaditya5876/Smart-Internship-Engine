
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schemas import RecRequest, RecItem
from app.services.deps import get_db, get_current_user
from app.services.recommendation_service import recommend_for_student

router = APIRouter()

@router.post("/recommend", response_model=List[RecItem])
def recommend(req: RecRequest, db: Session = Depends(get_db), user = Depends(get_current_user)):
    try:
        items = recommend_for_student(db, client_id=req.client_id, student_uid=req.student_uid, top_k=req.top_k)
        return items
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
