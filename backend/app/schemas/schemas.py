# from datetime import datetime
# from typing import List, Optional

# from pydantic import BaseModel, EmailStr, Field


# # -------- Auth / User --------

# class Token(BaseModel):
#     access_token: str
#     token_type: str = "bearer"


# class UserLogin(BaseModel):
#     email: str
#     password: str


# class UserBase(BaseModel):
#     email: str
#     role: str
#     client_id: Optional[str] = None


# class UserCreate(UserBase):
#     email: EmailStr
#     role: str
#     client_id: Optional[str] = None

#     # bcrypt only considers first 72 bytes -> enforce max 72 chars
#     password: str = Field(min_length=8, max_length=72)


# class UserOut(UserBase):
#     id: int
#     is_active: bool
#     created_at: datetime

#     class Config:
#         from_attributes = True


# # -------- Student --------

# class StudentBase(BaseModel):
#     student_uid: str
#     full_name: str
#     university: Optional[str] = None
#     degree: Optional[str] = None
#     semester: Optional[int] = None
#     cgpa: Optional[float] = None
#     skills: Optional[List[str]] = None
#     preferred_locations: Optional[List[str]] = None


# # -------- Student --------

# class StudentCreate(BaseModel):
#     # Make these optional so client doesn't have to send them
#     student_uid: Optional[str] = None
#     user_id: Optional[int] = None

#     full_name: str
#     university: Optional[str] = None
#     degree: Optional[str] = None
#     semester: Optional[int] = None
#     cgpa: Optional[float] = None
#     skills: Optional[List[str]] = None
#     preferred_locations: Optional[List[str]] = None


# class StudentUpdate(BaseModel):
#     full_name: Optional[str] = None
#     university: Optional[str] = None
#     degree: Optional[str] = None
#     semester: Optional[int] = None
#     cgpa: Optional[float] = None
#     skills: Optional[List[str]] = None
#     preferred_locations: Optional[List[str]] = None


# class StudentOut(StudentBase):
#     id: int
#     user_id: int
#     created_at: datetime

#     class Config:
#         from_attributes = True


# # -------- Job / Internship --------

# class JobBase(BaseModel):
#     job_uid: str
#     role: str
#     company: str
#     location: Optional[str] = None
#     required_skills: Optional[str] = None   # CSV or free-text; kept simple for now
#     description: Optional[str] = None
#     salary_min: Optional[float] = None
#     salary_max: Optional[float] = None
#     is_active: bool = True


# class JobCreate(BaseModel):
#     # Make optional so backend generates it
#     job_uid: Optional[str] = None

#     role: str
#     company: str
#     location: Optional[str] = None
#     required_skills: Optional[str] = None
#     description: Optional[str] = None
#     salary_min: Optional[float] = None
#     salary_max: Optional[float] = None
#     is_active: bool = True


# class JobUpdate(BaseModel):
#     role: Optional[str] = None
#     company: Optional[str] = None
#     location: Optional[str] = None
#     required_skills: Optional[str] = None
#     description: Optional[str] = None
#     salary_min: Optional[float] = None
#     salary_max: Optional[float] = None
#     is_active: Optional[bool] = None


# class JobOut(JobBase):
#     id: int
#     created_at: datetime

#     class Config:
#         from_attributes = True


# # -------- Recommendations --------

# class RecommendIn(BaseModel):
#     student_uid: str
#     top_k: int = 10


# class RecItem(BaseModel):
#     job_uid: str
#     role: str
#     company: str
#     score: float
#     required_skills: str
#     salary_min: Optional[float] = None
#     salary_max: Optional[float] = None


# class RecommendationResponse(BaseModel):
#     student_uid: str
#     items: List[RecItem]


# # -------- Feedback --------






#     class Config:
#         from_attributes = True

# # -------- Interactions --------





#     class Config:
#         from_attributes = True


# app/schemas/schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# -------- Auth / User --------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Optional[str] = None
    client_id: Optional[str] = None


class Login(BaseModel):
    email: str
    password: str


class UserBase(BaseModel):
    email: str
    role: str
    client_id: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    role: str
    client_id: Optional[str] = None
    password: str = Field(min_length=8, max_length=72)  # bcrypt limit


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -------- Student --------

class StudentBase(BaseModel):
    full_name: str
    university: Optional[str] = None
    degree: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    skills: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None


class StudentProfileIn(StudentBase):
    """
    Used by frontend for /students/me create/update.
    No user_id, no student_uid needed from the client.
    """
    pass


class StudentOut(StudentBase):
    id: int
    user_id: int
    student_uid: str
    created_at: datetime

    class Config:
        from_attributes = True


# -------- Job / Internship --------

class JobBase(BaseModel):
    role: str
    company: str
    location: Optional[str] = None
    required_skills: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_active: bool = True


class JobCreate(JobBase):
    """
    No job_uid required from client.
    """
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
    job_uid: str
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

class InteractionIn(BaseModel):
    student_uid: str
    job_uid: str
    event_type: str  # view/click/save/apply
    meta: Optional[str] = None

class InteractionOut(BaseModel):
    id: int
    student_id: int
    job_id: int
    event_type: str
    client_id: Optional[str] = None
    meta: Optional[str] = None
    timestamp: datetime