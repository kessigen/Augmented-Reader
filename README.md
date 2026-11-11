# Augmented Reader

![Augmented Reader logo](docs/images/logo.png)

**Augmented Reader** is a web application designed to provide an enhanced reading experience for readers by augmenting any ebook.

The app leverages 4 LLM tools (text summarization, image generation, metadata extraction and RAG querying ) to transform static books into interactive, enriched reading experiences.

![Reader interface](docs/images/reader-interface.jpg)

## Features
1. Previous chapter summarization
2. Increase and decrease text size
3. Character sheet display
4. Relationship graph
5. Background music
6. Book assistant
7. Scene image generation

See [FEATURES.md](docs/FEATURES.md) for details and screenshots of each feature.

## Architecture

![Architecture](docs/images/architecture.png)

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for diagrams of each module.

## Docs
- [Features](docs/FEATURES.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Tutorial + solving setup issues](docs/TUTORIAL.md)
- [Evaluation](eval/README.md)

## Structure
- `backend/` Django API
- `frontend/` Next.js app
- `docs/` features, architecture, tutorial and images
- `eval/` evaluation notebooks and results
- `samples/` sample epub (public domain)

## Prerequisites
- Python 3.12+
- Node.js 18+ (or 20+)

## Backend Setup (Django)
Initially slow, as it has to build all vector stores and DB structures
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
