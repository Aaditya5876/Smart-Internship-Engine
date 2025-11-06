from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# -------- Auth / User --------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Login(BaseModel):
    email: str
    password: str


class UserBase(BaseModel):
    email: str
    role: str
    client_id: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -------- Student --------

class StudentBase(BaseModel):
    student_uid: str
    full_name: str
    university: Optional[str] = None
    degree: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    skills: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None


class StudentCreate(StudentBase):
    user_id: int


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    university: Optional[str] = None
    degree: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    skills: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None


class StudentOut(StudentBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# -------- Job / Internship --------

class JobBase(BaseModel):
    job_uid: str
    role: str
    company: str
    location: Optional[str] = None
    required_skills: Optional[str] = None   # CSV or free-text; kept simple for now
    description: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_active: bool = True


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    required_skills: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_active: Optional[bool] = None


class JobOut(JobBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# -------- Recommendations --------

class RecommendIn(BaseModel):
    student_uid: str
    top_k: int = 10


class RecItem(BaseModel):
    job_uid: str
    role: str
    company: str
    score: float
    required_skills: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None


class RecommendationResponse(BaseModel):
    student_uid: str
    items: List[RecItem]


# -------- Feedback --------

class FeedbackIn(BaseModel):
    student_uid: str
    job_uid: str
    liked: bool
    notes: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    student_id: int
    job_id: int
    recommendation_id: Optional[int]
    liked: bool
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
