
# Smart Internship Engine — Thesis Build

## Quick Start (Local, with Postgres)

### 1) Start Postgres (Docker)
```bash
docker compose up -d
```
This runs Postgres on `localhost:5432` with user `postgres` / `postgres` and db `smart_intern_db`.

### 2) Seed a `.env`
```bash
cp .env.example .env
```

### 3) Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python -m app.db.init_db   # create tables and seed a few rows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4) Frontend
```bash
cd ../frontend
npm install
npm run dev
# open http://localhost:5173
```

### Login demo accounts
- **System Admin**: `admin@thesis.local` / `admin123`
- **University**: `uni@thesis.local` / `uni123`
- **Company**: `company@thesis.local` / `company123`
- **Student**: `student@thesis.local` / `student123`

> Replace `ml/models/backbone.pt` and `ml/models/heads/{client_id}.pt` with **your trained PFL** weights.
