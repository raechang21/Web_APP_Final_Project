# Web_APP_Final_Project

This project uses a separate frontend/backend architecture:
       
- `frontend/`: React + Vite
- `backend/`: FastAPI + SQLite

## Prerequisites

Make sure the following are installed on your machine:

- Node.js 18+ and `npm`
- Python 3.10+ and `pip`

Prepare your own API keys from Google AI Studio

## How to Run the Project

It is recommended to use two terminal windows: one for the backend and one for the frontend.

### 1. Start the Backend

Go into the backend directory, create a virtual environment, install dependencies, and create `.env`:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
mkdir var
```

Copy your API key to GEMINI_API_KEY in backend/.env

Start FastAPI:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

After the backend starts, you can verify it here:

```
http://localhost:8000/api/health
```

If it is working correctly, you should see:

```json
{"ok": true}
```

To verify that gemini is available:

```
http://localhost:8000/api/test-gemini
```

### 2. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Default frontend URL:

```text
http://localhost:5173
```

## Environment Variables

The backend `.env` can be based on `backend/.env.example`:

```env
SECRET_KEY=change-me-to-a-long-random-string
FRONTEND_ORIGIN=http://localhost:5173
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-3.1-flash-lite
SESSION_MAX_AGE=7200
```

For normal local development, these default values are usually enough.

## Default Ports

- Frontend: `5173`
- Backend: `8000`

Vite is already configured to proxy `/api` requests to `http://localhost:8000`, so once both frontend and backend are running, they should connect correctly.

## Common Issues

### 1. The frontend opens, but API requests fail

First, make sure the backend is running:

```text
http://localhost:8000/api/health
```

### 2. The database does not exist on first startup

This is normal. The backend will automatically create the SQLite database file on startup:

```text
backend/var/personality_paradox.db
```
