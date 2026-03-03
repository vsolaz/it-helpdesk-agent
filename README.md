# IT Helpdesk Agent

Conversational AI assistant for Mapfre Insurance that creates ServiceNow IT support tickets automatically.

## Architecture

```
┌─────────────────────┐     HTTPS      ┌──────────────────────────────┐
│   Angular 17 UI     │ ─────────── ▶  │   CloudFront + S3            │
│   (Mapfre branded)  │                │   (Static SPA hosting)       │
└─────────────────────┘                └──────────────────────────────┘
                                                  │
                                           POST /invoke
                                                  ▼
                                       ┌──────────────────────┐
                                       │   API Gateway         │
                                       │   (REST API)          │
                                       └──────────┬───────────┘
                                                  │
                                                  ▼
                                       ┌──────────────────────┐
                                       │   Lambda              │
                                       │   (Thin proxy)        │
                                       └──────────┬───────────┘
                                                  │
                              ┌───────────────────┼──────────────────┐
                              ▼                                      ▼
                   ┌─────────────────────┐              ┌────────────────────┐
                   │   DynamoDB           │              │   AgentCore Runtime │
                   │   (Session mapping)  │              │   (Strands Agent)   │
                   └─────────────────────┘              └─────────┬──────────┘
                                                                  │
                                          ┌───────────────────────┼──────────────────┐
                                          ▼                       ▼                  ▼
                                   ┌─────────────┐     ┌──────────────────┐  ┌──────────────┐
                                   │  Bedrock     │     │ Secrets Manager  │  │  ServiceNow  │
                                   │  Claude      │     │ (SN credentials) │  │  Table API   │
                                   │  Sonnet 4.6  │     └──────────────────┘  └──────────────┘
                                   └─────────────┘
```

## Components

| Component | Technology | Location |
|---|---|---|
| Frontend | Angular 17 SPA | S3 + CloudFront |
| API Layer | Lambda (Python 3.12) | API Gateway |
| Agent | Strands Agents + Claude Sonnet 4.6 | AgentCore Runtime |
| Sessions | DynamoDB (TTL) | us-east-1 |
| Secrets | AWS Secrets Manager | us-east-1 |
| Tickets | ServiceNow Table API | External |
| IaC | AWS CDK (Python) | `infra/` |

## Quick Start

### Local Development

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

### Deploy to AWS

**1. Build frontend:**
```bash
npx ng build --configuration production
```

**2. Deploy infrastructure:**
```bash
pip install aws-cdk-lib constructs
npx cdk bootstrap aws://ACCOUNT_ID/us-east-1
npx cdk deploy --all --app "python3 infra/app.py" --require-approval never
```

**3. Deploy agent to AgentCore:**
```bash
cd agentcore_strands
pip install bedrock-agentcore bedrock-agentcore-starter-toolkit
agentcore configure --entrypoint agent_main.py
agentcore deploy -auc -frd -env BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6 -env SERVICENOW_SECRET_NAME=helpdesk/servicenow
```

**4. Set ServiceNow credentials in Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name helpdesk/servicenow \
  --secret-string '{"instance_url":"https://YOUR_INSTANCE.service-now.com","username":"admin","password":"YOUR_PASSWORD"}' \
  --region us-east-1
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SERVICENOW_INSTANCE_URL` | Local only | — | ServiceNow instance URL |
| `SERVICENOW_USERNAME` | Local only | — | ServiceNow username |
| `SERVICENOW_PASSWORD` | Local only | — | ServiceNow password |
| `SERVICENOW_SECRET_NAME` | AWS | `helpdesk/servicenow` | Secrets Manager secret name |
| `BEDROCK_MODEL_ID` | No | `us.anthropic.claude-sonnet-4-6` | Bedrock model inference profile |
| `LLM_PROVIDER` | No | `bedrock` | `bedrock` or `openai` |
| `CORS_ORIGINS` | No | `http://localhost:4200` | Comma-separated allowed origins |

## Conversation Flow

```
User describes issue
        ↓
  Agent extracts fields (check_ticket_fields + save_ticket_field)
        ↓
  All fields collected?
   No → ask for missing fields
   Yes → confirm with user
        ↓
  User confirms?
   No → back to collect
   Yes → create_servicenow_ticket
        ↓
  Success → ticket number returned
  Error → offer retry
```

## Running Tests

```bash
source .venv/bin/activate
pytest agent/test_app.py -v
```

## Project Structure

```
├── agent/                    # Python backend (Lambda + local Flask)
│   ├── lambda_handler.py     # Lambda proxy to AgentCore
│   ├── app.py                # Flask app (local dev)
│   ├── graph.py              # LangGraph state machine (local)
│   └── nodes.py              # LangGraph nodes (local)
├── agentcore_strands/        # AgentCore Runtime agent
│   ├── agent_main.py         # Strands agent with ServiceNow tools
│   └── requirements.txt
├── infra/                    # CDK infrastructure
│   ├── app.py
│   └── stacks/
│       ├── backend_stack.py  # Lambda + API GW + DynamoDB
│       └── frontend_stack.py # S3 + CloudFront
├── src/                      # Angular frontend
│   └── app/
│       ├── components/       # Chat UI components
│       ├── services/         # Angular services
│       └── models/           # TypeScript interfaces
└── docs/
    └── architecture.excalidraw
```
