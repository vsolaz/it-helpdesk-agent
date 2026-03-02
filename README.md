# IT Helpdesk Agent

Conversational AI assistant that collects IT incident details and creates ServiceNow tickets automatically.

## Architecture

```
┌─────────────────────┐     HTTP      ┌──────────────────────────────┐
│   Angular 17 UI     │ ─────────── ▶ │   Flask API (Python)         │
│   (port 4200)       │               │   (port 8080)                │
└─────────────────────┘               └──────────┬───────────────────┘
                                                 │
                          ┌──────────────────────┼──────────────────┐
                          ▼                      ▼                  ▼
                    LangGraph Agent        ServiceNow API      Session Store
                    (collect → confirm      (create tickets)   (in-memory /
                     → submit flow)                            DynamoDB)
                          │
                    ┌─────┴─────┐
                    ▼           ▼
               AWS Bedrock   OpenAI
               (default)    (optional)
```

## Quick Start

### Local (manual)

**Backend:**
```bash
cp .env.example .env  # Fill in your values
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m flask --app agent/app run --port 8080
```

**Frontend:**
```bash
npm install
npx ng serve
```

Open http://localhost:4200

### Docker Compose

```bash
cp .env.example .env  # Fill in your values
docker compose up --build
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SERVICENOW_INSTANCE_URL` | ✅ | — | Your ServiceNow instance URL |
| `SERVICENOW_USERNAME` | ✅ | — | ServiceNow username |
| `SERVICENOW_PASSWORD` | ✅ | — | ServiceNow password |
| `LLM_PROVIDER` | ❌ | `bedrock` | `bedrock` or `openai` |
| `AWS_ACCESS_KEY_ID` | If Bedrock | — | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | If Bedrock | — | AWS secret key |
| `AWS_REGION` | If Bedrock | `us-east-1` | AWS region |
| `OPENAI_API_KEY` | If OpenAI | — | OpenAI API key |
| `CORS_ORIGINS` | ❌ | `http://localhost:4200` | Comma-separated allowed origins |

## Conversation Flow

```
User describes issue
        ↓
  collect_info (LLM extracts fields)
        ↓
  All fields collected?
   No → ask for missing fields
   Yes → confirm_ticket
        ↓
  User confirms?
   No → back to collect
   Yes → submit_ticket
        ↓
  Success → ticket number
  Error → handle_error (retry/cancel)
```

## Running Tests

```bash
pytest agent/test_app.py -v
```
