from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

DATABASE_URL = (
    f"postgresql+psycopg://{get_settings.POSTGRES_USER}:{get_settings.POSTGRES_PASSWORD}"
    f"@{get_settings.POSTGRES_HOST}:{get_settings.POSTGRES_PORT}/{get_settings.POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
