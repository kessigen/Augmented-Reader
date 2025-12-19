# Book Reader App (Monorepo)

## Structure
- `backend/` Django API
- `frontend/` Next.js app

## Prerequisites
- Python 3.12+
- Node.js 18+ (or 20+)

---

## Backend Setup (Django)
# initially will be slow as it has to build all vector stores and db structures
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
#in another terminal do:
cd frontend
npm install

npm run dev
