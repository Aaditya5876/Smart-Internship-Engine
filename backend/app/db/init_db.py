from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.models import User
from app.core.security import get_password_hash


def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Seed admin user if not present
    admin_email = "admin@example.com"
    existing = db.query(User).filter(User.email == admin_email).first()
    if not existing:
        admin = User(
            email=admin_email,
            password_hash=get_password_hash("Admin@123"),
            role="admin",
            client_id="admin-client",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("✅ Admin user created successfully.")
    else:
        print("ℹ️ Admin user already exists.")

    db.close()


if __name__ == "__main__":
    init_db()
