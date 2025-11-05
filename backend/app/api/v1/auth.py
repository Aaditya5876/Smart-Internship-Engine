
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.schemas import Login, Token, UserCreate, UserOut
from app.services.deps import get_db
from app.models.models import User
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email==data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(subject=user.email)
    return {"access_token": token}

@router.post("/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email==data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(email=data.email, hashed_password=get_password_hash(data.password), role=data.role, client_id=data.client_id)
    db.add(user); db.commit(); db.refresh(user)
    return user
