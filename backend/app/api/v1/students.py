from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session

from app.schemas.schemas import StudentCreate, StudentOut, StudentUpdate
from app.models.models import Student, User
from app.services.deps import (
    get_db,
    get_current_user,
    require_admin,
    require_student,
)
from app.services.cv_parser import extract_text_from_pdf, parse_cv_text

router = APIRouter(prefix="/students", tags=["students"])


def _list_to_raw(values):
    if not values:
        return None
    return ",".join(values)


def _raw_to_list(raw):
    if not raw:
        return None
    return [s.strip() for s in raw.split(",") if s.strip()]


@router.post("/", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a student profile.

    - If current user is a STUDENT: profile is always linked to their own user_id.
    - If current user is ADMIN: user_id from payload is used.
    """
    if current_user.role not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students or admins can create student profiles",
        )

    existing = db.query(Student).filter(Student.student_uid == payload.student_uid).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="student_uid already exists",
        )

    if current_user.role == "student":
        user_id = current_user.id
    else:
        # admin
        user_id = payload.user_id

    student = Student(
        user_id=user_id,
        student_uid=payload.student_uid,
        full_name=payload.full_name,
        university=payload.university,
        degree=payload.degree,
        semester=payload.semester,
        cgpa=payload.cgpa,
        skills_raw=_list_to_raw(payload.skills),
        preferred_locations_raw=_list_to_raw(payload.preferred_locations),
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return StudentOut(
        id=student.id,
        user_id=student.user_id,
        student_uid=student.student_uid,
        full_name=student.full_name,
        university=student.university,
        degree=student.degree,
        semester=student.semester,
        cgpa=student.cgpa,
        skills=_raw_to_list(student.skills_raw),
        preferred_locations=_raw_to_list(student.preferred_locations_raw),
        created_at=student.created_at,
    )


@router.get("/", response_model=List[StudentOut])
def list_students(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    List all students – ADMIN only.
    """
    students = db.query(Student).all()
    return [
        StudentOut(
            id=s.id,
            user_id=s.user_id,
            student_uid=s.student_uid,
            full_name=s.full_name,
            university=s.university,
            degree=s.degree,
            semester=s.semester,
            cgpa=s.cgpa,
            skills=_raw_to_list(s.skills_raw),
            preferred_locations=_raw_to_list(s.preferred_locations_raw),
            created_at=s.created_at,
        )
        for s in students
    ]


@router.get("/{student_uid}", response_model=StudentOut)
def get_student(
    student_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.query(Student).filter(Student.student_uid == student_uid).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    # Only admin or owner student can view
    if current_user.role != "admin" and s.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this student",
        )

    return StudentOut(
        id=s.id,
        user_id=s.user_id,
        student_uid=s.student_uid,
        full_name=s.full_name,
        university=s.university,
        degree=s.degree,
        semester=s.semester,
        cgpa=s.cgpa,
        skills=_raw_to_list(s.skills_raw),
        preferred_locations=_raw_to_list(s.preferred_locations_raw),
        created_at=s.created_at,
    )


@router.put("/{student_uid}", response_model=StudentOut)
def update_student(
    student_uid: str,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.query(Student).filter(Student.student_uid == student_uid).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    # Only admin or owner student can update
    if current_user.role != "admin" and s.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this student",
        )

    if payload.full_name is not None:
        s.full_name = payload.full_name
    if payload.university is not None:
        s.university = payload.university
    if payload.degree is not None:
        s.degree = payload.degree
    if payload.semester is not None:
        s.semester = payload.semester
    if payload.cgpa is not None:
        s.cgpa = payload.cgpa
    if payload.skills is not None:
        s.skills_raw = _list_to_raw(payload.skills)
    if payload.preferred_locations is not None:
        s.preferred_locations_raw = _list_to_raw(payload.preferred_locations)

    db.commit()
    db.refresh(s)

    return StudentOut(
        id=s.id,
        user_id=s.user_id,
        student_uid=s.student_uid,
        full_name=s.full_name,
        university=s.university,
        degree=s.degree,
        semester=s.semester,
        cgpa=s.cgpa,
        skills=_raw_to_list(s.skills_raw),
        preferred_locations=_raw_to_list(s.preferred_locations_raw),
        created_at=s.created_at,
    )


@router.delete("/{student_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_uid: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Delete student profile – ADMIN only.
    """
    s = db.query(Student).filter(Student.student_uid == student_uid).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    db.delete(s)
    db.commit()
    return None

@router.post("/upload-cv", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student),
):
    """
    Upload a CV (PDF), parse it, and create or update the student's profile.

    - Only users with role 'student' can call this.
    - If a Student profile already exists for this user, we update missing fields.
    - Otherwise, we create a new Student entry with a generated student_uid.
    """
    # 1. Extract raw text from CV
    text = extract_text_from_pdf(file)

    # 2. Parse structured fields
    parsed = parse_cv_text(text)

    # 3. Find or create student profile
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    creating = False

    if not student:
        creating = True
        student = Student(
            user_id=current_user.id,
            student_uid=f"stu_{current_user.id}",  # simple deterministic uid
        )

    # 4. Apply parsed values (do not blindly overwrite everything)
    if parsed.get("full_name") and not student.full_name:
        student.full_name = parsed["full_name"]

    if parsed.get("degree"):
        student.degree = parsed["degree"]

    if parsed.get("university"):
        student.university = parsed["university"]

    if parsed.get("cgpa") is not None:
        student.cgpa = parsed["cgpa"]

    skills = parsed.get("skills") or []
    if skills:
        # If there are existing skills, merge them; else just set parsed skills
        existing = _raw_to_list(student.skills_raw) or []
        merged = sorted(set(existing) | set(skills))
        student.skills_raw = _list_to_raw(merged)

    if creating:
        db.add(student)

    db.commit()
    db.refresh(student)

    return StudentOut(
        id=student.id,
        user_id=student.user_id,
        student_uid=student.student_uid,
        full_name=student.full_name,
        university=student.university,
        degree=student.degree,
        semester=student.semester,
        cgpa=student.cgpa,
        skills=_raw_to_list(student.skills_raw),
        preferred_locations=_raw_to_list(student.preferred_locations_raw),
        created_at=student.created_at,
    )
