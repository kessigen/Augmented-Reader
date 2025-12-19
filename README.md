# Book Reader App (Monorepo)

## Structure
- `backend/` Django API
- `frontend/` Next.js app

## Prerequisites
- Python 3.12+
- Node.js 18+ (or 20+)

---

## Backend Setup (Django)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
# Edit backend/.env with real values

python manage.py migrate
python manage.py runserver


## Frontend  Setup (Django)
cd frontend
npm install

Copy-Item .env.example .env.local
npm run dev