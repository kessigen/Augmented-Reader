# Book Reader App 
Link to features + eval code + tutorial: https://drive.google.com/drive/folders/1WPHCgcoTJ9fmbo3yVLAgOuJV9nqq6AUF?usp=sharing
## Structure
- `backend/` Django API
- `frontend/` Next.js app

## Prerequisites
- Python 3.12+
- Node.js 18+ (or 20+)

---

## Backend Setup (Django)
# Initially slow, as it has to build all vector stores and DB structures
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
# Edit backend/.env with real values

python manage.py migrate
python manage.py runserver
```

## Frontend Setup (Next.js)
In another terminal:
```powershell
cd frontend
npm install

npm run dev
```
