
import numpy as np
from sqlalchemy.orm import Session
from app.models.models import Student, Job, Recommendation
from app.ml.inference import PFLRegistry
from typing import List, Dict

def compute_skill_overlap(student_skills: str, job_skills: str) -> int:
    s = {t.strip().lower() for t in (student_skills or '').split(',') if t.strip()}
    j = {t.strip().lower() for t in (job_skills or '').split(',') if t.strip()}
    return len(s & j)

def role_flags(role: str):
    r = (role or '').lower()
    return [
        int(any(k in r for k in ['front-end','frontend','ui'])),
        int(any(k in r for k in ['back-end','backend','api'])),
        int(any(k in r for k in ['data','ml','ai'])),
        0
    ]

def build_features(student: Student, jobs: List[Job]) -> np.ndarray:
    rows = []
    for jb in jobs:
        overlap = compute_skill_overlap(student.skills, jb.required_skills)
        flags = role_flags(jb.role)
        rows.append([
            float(student.gpa or 0.0),
            int(student.age or 0),
            float(jb.salary_min or 0.0),
            float(jb.salary_max or 0.0),
            overlap, *flags
        ])
    return np.array(rows, dtype=float)

def recommend_for_student(db: Session, client_id: str, student_uid: str, top_k: int = 10):
    student = db.query(Student).filter(Student.student_uid==student_uid).first()
    if not student:
        raise ValueError("Student not found")

    jobs = db.query(Job).all()
    feats = build_features(student, jobs)
    registry = PFLRegistry()
    scores = registry.predict(client_id, feats)

    # store/update recommendations
    items = []
    for jb, sc in zip(jobs, scores):
        items.append((jb, float(sc)))
    items.sort(key=lambda x: x[1], reverse=True)
    items = items[:top_k]

    recs = []
    for jb, sc in items:
        # upsert on (student, job)
        existing = db.query(Recommendation).filter(
            Recommendation.student_id == student.id,
            Recommendation.job_id == jb.id
        ).first()
        if existing:
            existing.score = sc
            recs.append(existing)
        else:
            obj = Recommendation(student_id=student.id, job_id=jb.id, score=sc)
            db.add(obj); db.flush()
            recs.append(obj)

    db.commit()
    # return dicts
    return [{
        "job_uid": jb.job_uid,
        "role": jb.role,
        "company": jb.company,
        "required_skills": jb.required_skills,
        "salary_min": jb.salary_min,
        "salary_max": jb.salary_max,
        "score": sc
    } for jb, sc in [(db.query(Job).get(r.job_id), r.score) for r in recs]]
