from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1 import auth, students, jobs, recs, feedback, ml, fl, interactions

settings = get_settings  # ✅ CALL IT

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "Backend is up and running!"}

app.include_router(auth.router, prefix="/api/v1")
app.include_router(students.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(recs.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(ml.router, prefix="/api/v1")
app.include_router(fl.router, prefix="/api/v1")
app.include_router(interactions.router, prefix="/api/v1")
