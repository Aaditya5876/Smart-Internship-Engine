from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    # Postgres settings
    POSTGRES_USER: str = "internship_user_test"
    POSTGRES_PASSWORD: str = "StrongPassword123"
    POSTGRES_DB: str = "internship_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    APP_NAME: str = "Smart Internship Backend"
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Security (for later, JWT etc.)
    SECRET_KEY: str = "supersecret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 

    class Config:
        env_file = ".env"   # root .env


get_settings = Settings()
