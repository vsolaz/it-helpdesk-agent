# IT Helpdesk Agent

Conversational AI assistant for Mapfre Insurance that creates ServiceNow IT support tickets automatically.

## Architecture

```
┌─────────────────────┐     HTTPS      ┌──────────────────────────────┐
│   User (Browser)    │ ─────────── ▶  │   CloudFront + S3            │
│                     │                │   (Angular SPA)              │
└─────────────────────┘                └──────────────────────────────┘
                                                  │
                                    Cognito Auth + POST /invoke
                                                  ▼
                                       ┌──────────────────────┐
                                       │   API Gateway         │
                                       └──────────┬───────────┘
                                                  ▼
                                       ┌──────────────────────┐
                                       │   Lambda (proxy)      │
                                       └──────────┬───────────┘
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
| Auth | Cognito User Pool | Custom login form |
| API Layer | Lambda (Python 3.12) | API Gateway |
| Agent | Strands Agents + Claude Sonnet 4.6 | AgentCore Runtime |
| Sessions | DynamoDB (TTL) | us-east-1 |
| Secrets | AWS Secrets Manager | us-east-1 |
| Tickets | ServiceNow Table API | External |
| IaC | AWS CDK (Python) | `infra/` |

## Quick Start

### Local Development

```bash
cp .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m flask --app agent/app run --port 8080
```

```bash
npm install && npx ng serve
```

Open http://localhost:4200

### Deploy to AWS

```bash
npx ng build --configuration production
npx cdk deploy --all --app "python3 infra/app.py" --require-approval never
```

### Deploy Agent to AgentCore

```bash
cd agentcore_strands
agentcore configure --entrypoint agent_main.py
agentcore deploy -auc -frd -env BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6 -env SERVICENOW_SECRET_NAME=helpdesk/servicenow
```

### Create Cognito User

```bash
aws cognito-idp admin-create-user \
  --user-pool-id USER_POOL_ID \
  --username user@example.com \
  --temporary-password TempPass123! \
  --user-attributes Name=email,Value=user@example.com Name=email_verified,Value=true \
  --region us-east-1
```

## Running Tests

```bash
pytest agent/test_app.py -v
```
