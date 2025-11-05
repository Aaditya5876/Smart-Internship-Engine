
from fastapi import APIRouter
from . import auth, students, jobs, recs, feedback

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(students.router, prefix="/students", tags=["students"])
router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
router.include_router(recs.router, prefix="/recs", tags=["recs"])
router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
