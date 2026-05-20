# Web_APP_Final_Project

This project uses a separate frontend/backend architecture:
       
- `frontend/`: React + Vite
- `backend/`: FastAPI + SQLite
- The chatbot feature also depends on a local `Ollama` service

## Prerequisites

Make sure the following are installed on your machine:

- Node.js 18+ and `npm`
- Python 3.10+ and `pip`
- `Ollama` if you want to use the chatbot feature

## How to Run the Project

It is recommended to use two terminal windows: one for the backend and one for the frontend.

### 1. Start the Backend

Go into the backend directory, create a virtual environment, install dependencies, and create `.env`:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

After the backend starts, you can verify it here:

```text
http://localhost:8000/api/health
```

If it is working correctly, you should see:

```json
{"ok": true}
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

## Extra Setup for the Chatbot

The chatbot feature uses a local Ollama service. The default model is `gemma3:4b`. If you want to use the chatbot page, first run:

```bash
ollama serve
```

Then download the model:

```bash
ollama pull gemma3:4b
```

To verify that Ollama is available:

```text
http://localhost:8000/api/test-ollama
```

## Environment Variables

The backend `.env` can be based on `backend/.env.example`:

```env
SECRET_KEY=change-me-to-a-long-random-string
FRONTEND_ORIGIN=http://localhost:5173
DATABASE_URL=sqlite:///./personality_paradox.db
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
SESSION_MAX_AGE=7200
```

For normal local development, these default values are usually enough.

## Default Ports

- Frontend: `5173`
- Backend: `8000`
- Ollama: `11434`

Vite is already configured to proxy `/api` requests to `http://localhost:8000`, so once both frontend and backend are running, they should connect correctly.

## Common Issues

### 1. The frontend opens, but API requests fail

First, make sure the backend is running:

```text
http://localhost:8000/api/health
```

### 2. The chatbot says it cannot connect to Ollama

Check the following:

- Ollama is installed
- `ollama serve` is running
- `gemma3:4b` has been downloaded

### 3. The database does not exist on first startup

This is normal. The backend will automatically create the SQLite database file on startup:

```text
backend/personality_paradox.db
```
