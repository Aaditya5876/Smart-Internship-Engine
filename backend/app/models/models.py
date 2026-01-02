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
    password_hash = Column(String(500), nullable=False)
    role = Column(String(20), nullable=False)
    client_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="user", uselist=False)


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # external identifier used in APIs / FL client mapping
    student_uid = Column(String(100), unique=True, nullable=False, index=True)

    full_name = Column(String(255), nullable=False)
    university = Column(String(255), nullable=True)
    degree = Column(String(255), nullable=True)
    semester = Column(Integer, nullable=True)
    cgpa = Column(Double, nullable=True)

    # store comma-separated skills and locations; API layer can expose them as lists if needed
    skills_raw = Column(Text, nullable=True)
    preferred_locations_raw = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="student")
    recommendations = relationship(
        "Recommendation",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    feedback = relationship(
        "Feedback",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    interactions = relationship(
        "Interaction",
        back_populates="student",
        cascade="all, delete-orphan",
    )


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    # external identifier used in APIs / FL client mapping
    job_uid = Column(String(100), unique=True, nullable=False, index=True)

    role = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)

    required_skills = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    salary_min = Column(Double, nullable=True)
    salary_max = Column(Double, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    recommendations = relationship(
        "Recommendation",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    feedback = relationship(
        "Feedback",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    interactions = relationship(
        "Interaction",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    score = Column(Numeric(10, 6), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="recommendations")
    job = relationship("Job", back_populates="recommendations")

    # if using Alembic later you can add a unique constraint:
    # UniqueConstraint("student_id", "job_id")

class Interaction(Base):
    """User→Job interaction log.

    This table is the core signal used for both:
    1) Online analytics (what users did)
    2) Offline training (implicit feedback / negative sampling)

    event_type examples: view, click, save, apply
    """

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)

    event_type = Column(String(50), nullable=False, index=True)
    client_id = Column(String(50), nullable=True, index=True)
    meta = Column(Text, nullable=True)

    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)

    student = relationship("Student", back_populates="interactions")
    job = relationship("Job", back_populates="interactions")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True)
    liked = Column(Boolean, nullable=False)  # True = liked/applied, False = skipped
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="feedback")
    job = relationship("Job", back_populates="feedback")
    recommendation = relationship("Recommendation")
