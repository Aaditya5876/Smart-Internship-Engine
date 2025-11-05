
from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Login(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    role: str
    client_id: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    role: str
    client_id: Optional[str] = None
    class Config:
        from_attributes = True

class StudentIn(BaseModel):
    student_uid: str
    name: str
    age: int
    gpa: float
    skills: str
    client_id: str

class StudentOut(StudentIn):
    id: int
    class Config:
        from_attributes = True

class JobIn(BaseModel):
    job_uid: str
    role: str
    company: str
    required_skills: str
    salary_min: float
    salary_max: float
    industry: str
    work_type: str
    client_id: str

class JobOut(JobIn):
    id: int
    class Config:
        from_attributes = True

class RecRequest(BaseModel):
    client_id: str
    student_uid: str
    top_k: int = 10

class RecItem(BaseModel):
    job_uid: str
    role: str
    company: str
    score: float
    required_skills: str
    salary_min: float
    salary_max: float

class FeedbackIn(BaseModel):
    student_uid: str
    job_uid: str
    liked: bool
    notes: Optional[str] = None
