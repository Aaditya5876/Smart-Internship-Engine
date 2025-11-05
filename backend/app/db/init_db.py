from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.models import User, University, Company
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db() -> None:
    print("👉 Creating tables (if not exist)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ---- seed admin user ----
        admin_email = "admin@internship.local"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                password_hash=pwd_context.hash("Admin123!"),  # change later
                role="admin",
                is_active=True,
            )
            db.add(admin)
            print(f"✅ Admin user created: {admin_email}")

        # ---- seed universities ----
        islington = db.query(University).filter(University.client_id == "client_U1").first()
        if not islington:
            islington = University(
                name="Islington College",
                client_id="client_U1",
                country="Nepal",
                city="Kathmandu",
            )
            db.add(islington)
            print("✅ University created: Islington College (client_U1)")

        london_met = db.query(University).filter(University.client_id == "client_U2").first()
        if not london_met:
            london_met = University(
                name="London Metropolitan University",
                client_id="client_U2",
                country="United Kingdom",
                city="London",
            )
            db.add(london_met)
            print("✅ University created: London Metropolitan University (client_U2)")

        # ---- seed example company ----
        company = db.query(Company).filter(Company.client_id == "client_C1").first()
        if not company:
            company = Company(
                name="TechCorp",
                client_id="client_C1",
                industry="IT",
                country="Nepal",
                city="Kathmandu",
            )
            db.add(company)
            print("✅ Company created: TechCorp (client_C1)")

        db.commit()
        print("🎉 DB initialization & seeding completed.")
    except Exception as e:
        db.rollback()
        print("❌ Error during init_db:", e)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
