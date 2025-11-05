from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Numeric,
    Text,
    TIMESTAMP,
    Double,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # student | university | company | admin
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="user", uselist=False)


class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    client_id = Column(String(50), unique=True, nullable=False)  # e.g. client_U1
    country = Column(String(100))
    city = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    students = relationship("Student", back_populates="university")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    client_id = Column(String(50), unique=True, nullable=False)  # e.g. client_C1
    industry = Column(String(100))
    country = Column(String(100))
    city = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    jobs = relationship("Job", back_populates="company")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"))
    external_student_id = Column(String(50))  # if you need to map to ML dataset
    full_name = Column(String(255), nullable=False)
    gpa = Column(Numeric(3, 2))
    age = Column(Integer)
    major = Column(String(255))
    skills_raw = Column(Text)  # comma-separated skills from UI
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="student")
    university = relationship("University", back_populates="students")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    job_code = Column(String(50))  # optional external id
    title = Column(String(255), nullable=False)
    description = Column(Text)
    role_type = Column(String(50))     # frontend | backend | data | other
    work_type = Column(String(50))     # onsite | remote | hybrid
    salary_min = Column(Numeric(10, 2))
    salary_max = Column(Numeric(10, 2))
    required_skills = Column(Text)
    industry = Column(String(100))
    location = Column(String(255))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="jobs")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    score = Column(Numeric(10, 6), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # simple unique constraint (student, job)
    # if using Alembic later we can add: UniqueConstraint("student_id", "job_id")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"))
    liked = Column(Boolean, nullable=False)  # True = liked/applied, False = skipped
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
