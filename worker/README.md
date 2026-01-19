# Aetheris Worker - Railway Deployment

Webhook-based code analysis worker for GitHub repositories.

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/aetheris)

### Manual Setup

1. **Create Railway Project**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login and create project
   railway login
   railway init
   ```

2. **Set Environment Variables** (Railway Dashboard → Variables)
   ```
   GITHUB_TOKEN=ghp_xxxxxxxxxxxx
   GITHUB_WEBHOOK_SECRET=your-webhook-secret
   GEMINI_API_KEY=your-gemini-api-key
   ANALYSIS_TIMEOUT=3600
   ```

3. **Deploy**
   ```bash
   railway up
   ```

4. **Configure GitHub Webhook**
   - Go to your repo → Settings → Webhooks → Add webhook
   - Payload URL: `https://your-app.railway.app/webhook/github`
   - Content type: `application/json`
   - Secret: Same as `GITHUB_WEBHOOK_SECRET`
   - Events: Select "Push" and "Pull requests"

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub token with repo access |
| `GITHUB_WEBHOOK_SECRET` | Yes | Secret for webhook signature verification |
| `GEMINI_API_KEY` | Yes | Google AI API key |
| `ANALYSIS_TIMEOUT` | No | Timeout in seconds (default: 3600) |
| `PORT` | No | Port to listen on (default: 8080, set by Railway) |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check with job count |
| `/health` | GET | Simple health check |
| `/webhook/github` | POST | GitHub webhook receiver |
| `/jobs` | GET | List all analysis jobs |
| `/jobs/{job_id}` | GET | Get specific job status |

## Webhook Events Handled

- **push** → Analyzes main/master branch pushes
- **pull_request** → Analyzes PR on open/sync/reopen
- **ping** → Responds with pong (webhook test)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn httpx

# Set environment variables
export GITHUB_TOKEN=ghp_xxx
export GEMINI_API_KEY=xxx

# Run worker
python -m uvicorn worker.app:app --reload --port 8080

# Test with ngrok for webhook testing
ngrok http 8080
```

## Architecture

```
GitHub Webhook → Railway Worker → Clone Repo → Run Aetheris → Post Results
                     ↓
              FastAPI (async)
                     ↓
         Background Task Queue
```
