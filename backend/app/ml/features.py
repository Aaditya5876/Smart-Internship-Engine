# app/ml/features.py
from typing import Dict, List, Tuple, Optional

import numpy as np
from sqlalchemy.orm import Session

from app.models.models import Student, Job, Feedback


def _split_skills(text: Optional[str]) -> List[str]:
    if not text:
        return []
    # we assume comma-separated or space-separated skills
    parts = []
    for chunk in text.replace(";", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts.extend(chunk.lower().split())
    return list(set(parts))  # unique


def build_skill_vocab(db: Session) -> Dict[str, int]:
    vocab = {}
    idx = 0

    # from students
    students = db.query(Student).all()
    for s in students:
        skills = _split_skills(s.skills_raw)
        for sk in skills:
            if sk not in vocab:
                vocab[sk] = idx
                idx += 1

    # from jobs
    jobs = db.query(Job).all()
    for j in jobs:
        skills = _split_skills(j.required_skills)
        for sk in skills:
            if sk not in vocab:
                vocab[sk] = idx
                idx += 1

    return vocab


def encode_student(student: Student, vocab: Dict[str, int]) -> np.ndarray:
    v = np.zeros(len(vocab) + 2, dtype=np.float32)  # skills + [cgpa, bias]

    # skills
    for sk in _split_skills(student.skills_raw):
        if sk in vocab:
            v[vocab[sk]] = 1.0

    # cgpa
    cgpa_idx = len(vocab)
    v[cgpa_idx] = float(student.cgpa or 0.0)

    # bias term
    v[cgpa_idx + 1] = 1.0
    return v


def encode_job(job: Job, vocab: Dict[str, int]) -> np.ndarray:
    v = np.zeros(len(vocab) + 3, dtype=np.float32)  # skills + [salary_min, salary_max, bias]

    for sk in _split_skills(job.required_skills):
        if sk in vocab:
            v[vocab[sk]] = 1.0

    base = len(vocab)
    v[base] = float(job.salary_min or 0.0)
    v[base + 1] = float(job.salary_max or 0.0)
    v[base + 2] = 1.0  # bias
    return v


def build_feature_vector(student: Student, job: Job, vocab: Dict[str, int]) -> np.ndarray:
    s_vec = encode_student(student, vocab)
    j_vec = encode_job(job, vocab)
    return np.concatenate([s_vec, j_vec], axis=0)


def get_student_feedback_dataset(
    db: Session,
    student: Student,
    vocab: Dict[str, int],
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Builds (X, y) for a given student from Feedback table.
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
        x = build_feature_vector(student, job, vocab)
        X_list.append(x)
        y_list.append(1.0 if fb.liked else 0.0)

    X = np.stack(X_list).astype(np.float32)
    y = np.array(y_list, dtype=np.float32)
    return X, y
