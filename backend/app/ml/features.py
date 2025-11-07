# app/ml/features.py

from typing import Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.models.models import Student, Job, Feedback
from app.ml.embeddings import encode_texts, get_embedding_dim


def _student_text(student: Student) -> str:
    """
    Build a single text string describing the student.
    Works for IT, management, banking, etc.
    """
    parts = []

    if student.full_name:
        parts.append(student.full_name)

    if student.degree:
        parts.append(student.degree)

    if student.university:
        parts.append(student.university)

    if student.skills_raw:
        parts.append(student.skills_raw)

    if student.preferred_locations_raw:
        parts.append("prefers locations: " + student.preferred_locations_raw)

    if student.cgpa is not None:
        parts.append(f"CGPA {student.cgpa}")

    return " ; ".join(parts)


def _job_text(job: Job) -> str:
    """
    Build a single text string describing the job/internship.
    Again, domain-agnostic.
    """
    parts = []

    if job.role:
        parts.append(job.role)

    if job.company:
        parts.append(job.company)

    if job.location:
        parts.append(job.location)

    if job.required_skills:
        parts.append("skills: " + job.required_skills)

    if job.description:
        parts.append(job.description)

    if job.salary_min is not None or job.salary_max is not None:
        parts.append(f"salary range {job.salary_min} to {job.salary_max}")

    return " ; ".join(parts)


def build_pair_features(student: Student, job: Job) -> np.ndarray:
    """
    Encode (student, job) as a semantic feature vector.

    We:
    - encode student_text and job_text into sentence embeddings s, j
    - build concatenation [s, j, |s-j|, s*j]

    This is a very standard matching architecture used in industrial recommenders.
    """
    s_text = _student_text(student)
    j_text = _job_text(job)

    embs = encode_texts([s_text, j_text])
    s_vec = embs[0]  # (D,)
    j_vec = embs[1]  # (D,)

    diff = np.abs(s_vec - j_vec)
    prod = s_vec * j_vec

    pair = np.concatenate([s_vec, j_vec, diff, prod], axis=0)  # shape (4D,)
    pair = pair.astype(np.float32)
    return pair


def get_input_dim() -> int:
    """
    Total input dimension to the PFL model = 4 * embedding_dim.
    """
    d = get_embedding_dim()
    return 4 * d


def get_student_feedback_dataset(
    db: Session,
    student: Student,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build (X, y) for one student from Feedback table using semantic features.

    y = 1 if liked=True, 0 otherwise.
    """
    q = (
        db.query(Feedback, Job)
        .join(Job, Feedback.job_id == Job.id)
        .filter(Feedback.student_id == student.id)
    )
    rows = q.all()
    if not rows:
        return np.empty((0, 1), dtype=np.float32), np.empty((0,), dtype=np.float32)

    X_list = []
    y_list = []

    for fb, job in rows:
        x = build_pair_features(student, job)
        X_list.append(x)
        y_list.append(1.0 if fb.liked else 0.0)

    X = np.stack(X_list).astype(np.float32)
    y = np.array(y_list, dtype=np.float32)
    return X, y
