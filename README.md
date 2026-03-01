# IT Helpdesk Agent

Conversational AI assistant for creating ServiceNow IT support tickets.

## Architecture

- **Frontend**: Angular 17 chat UI (`src/`)
- **Backend**: Python Flask + LangGraph agent (`agent/`)

## Quick Start

### Backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m flask --app agent/app run --port 8080
```

### Frontend
```bash
npm install
npx ng serve
```

Open http://localhost:4200
