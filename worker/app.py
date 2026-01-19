"""
Aetheris Worker - FastAPI webhook handler for GitHub events.

This worker receives GitHub webhooks and triggers Aetheris code analysis.
Deploy to Railway as a separate service.

Environment Variables Required:
- GITHUB_TOKEN: GitHub token for cloning repos and posting comments
- GITHUB_WEBHOOK_SECRET: Secret for verifying webhook signatures
- GEMINI_API_KEY: Google AI API key for analysis
- PORT: Port to listen on (default: 8080, set by Railway)
"""

import asyncio
import hashlib
import hmac
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

app = FastAPI(
    title="Aetheris Worker",
    description="GitHub webhook handler for AI code analysis",
    version="1.0.0",
)

# Configuration from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANALYSIS_TIMEOUT = int(os.getenv("ANALYSIS_TIMEOUT", "3600"))  # 1 hour default


class WebhookPayload(BaseModel):
    """Generic webhook payload."""
    action: Optional[str] = None
    repository: Optional[Dict[str, Any]] = None
    pull_request: Optional[Dict[str, Any]] = None
    ref: Optional[str] = None
    after: Optional[str] = None
    before: Optional[str] = None
    commits: Optional[list] = None
    sender: Optional[Dict[str, Any]] = None


class AnalysisJob:
    """Represents an analysis job."""

    def __init__(
        self,
        repo_url: str,
        branch: str,
        commit_sha: str,
        pr_number: Optional[int] = None,
        repo_full_name: str = "",
    ):
        self.repo_url = repo_url
        self.branch = branch
        self.commit_sha = commit_sha
        self.pr_number = pr_number
        self.repo_full_name = repo_full_name
        self.status = "pending"
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None


# In-memory job tracking (use Redis in production)
active_jobs: Dict[str, AnalysisJob] = {}


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature."""
    if not GITHUB_WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured

    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


async def run_analysis(job: AnalysisJob) -> None:
    """Run Aetheris analysis on a repository."""
    job.status = "running"
    job.started_at = datetime.utcnow()

    temp_dir = None
    try:
        # Create temp directory for clone
        temp_dir = tempfile.mkdtemp(prefix="aetheris_")

        # Clone repository
        clone_url = job.repo_url.replace(
            "https://github.com/",
            f"https://x-access-token:{GITHUB_TOKEN}@github.com/"
        )

        clone_cmd = [
            "git", "clone",
            "--depth", "1",
            "--branch", job.branch,
            clone_url,
            temp_dir
        ]

        subprocess.run(clone_cmd, check=True, capture_output=True, timeout=300)

        # Run Aetheris analysis
        analysis_cmd = [
            "aetheris", "analysis",
            "--profile", "ci",
            "--timeout", f"{ANALYSIS_TIMEOUT}s",
        ]

        if job.pr_number:
            analysis_cmd.extend(["--pr", str(job.pr_number)])

        env = os.environ.copy()
        env["GEMINI_API_KEY"] = GEMINI_API_KEY
        env["GITHUB_TOKEN"] = GITHUB_TOKEN

        result = subprocess.run(
            analysis_cmd,
            cwd=temp_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=ANALYSIS_TIMEOUT,
        )

        # Post results to GitHub
        if job.pr_number:
            await post_pr_comment(job, result)
        else:
            await update_commit_status(job, result)

        job.status = "completed"

    except subprocess.TimeoutExpired:
        job.status = "failed"
        job.error = "Analysis timed out"
    except subprocess.CalledProcessError as e:
        job.status = "failed"
        job.error = f"Command failed: {e.stderr}"
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
    finally:
        job.completed_at = datetime.utcnow()
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


async def post_pr_comment(job: AnalysisJob, result: subprocess.CompletedProcess) -> None:
    """Post analysis results as a PR comment."""
    import httpx

    # Parse analysis results from stdout
    summary = result.stdout[:4000] if result.stdout else "Analysis completed."
    if result.returncode != 0 and result.stderr:
        summary += f"\n\n**Warnings:**\n```\n{result.stderr[:1000]}\n```"

    comment_body = f"""## 🔍 Aetheris Analysis Complete

{summary}

---
*Analysis by [Aetheris](https://github.com/adryserage/aetheris) Worker*
"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{job.repo_full_name}/issues/{job.pr_number}/comments",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={"body": comment_body},
        )
        response.raise_for_status()


async def update_commit_status(job: AnalysisJob, result: subprocess.CompletedProcess) -> None:
    """Update commit status on GitHub."""
    import httpx

    state = "success" if result.returncode == 0 else "failure"
    description = "Analysis completed" if state == "success" else "Analysis found issues"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{job.repo_full_name}/statuses/{job.commit_sha}",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={
                "state": state,
                "description": description[:140],
                "context": "aetheris/analysis",
            },
        )
        response.raise_for_status()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "aetheris-worker",
        "status": "healthy",
        "active_jobs": len([j for j in active_jobs.values() if j.status == "running"]),
    }


@app.get("/health")
async def health():
    """Health check for Railway."""
    return {"status": "ok"}


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
):
    """Handle GitHub webhook events."""

    # Verify signature
    body = await request.body()
    if x_hub_signature_256 and not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    # Handle different event types
    if x_github_event == "push":
        return await handle_push_event(payload, background_tasks)
    elif x_github_event == "pull_request":
        return await handle_pr_event(payload, background_tasks)
    elif x_github_event == "ping":
        return {"message": "pong"}
    else:
        return {"message": f"Event '{x_github_event}' not handled"}


async def handle_push_event(payload: dict, background_tasks: BackgroundTasks):
    """Handle push events."""
    repo = payload.get("repository", {})
    repo_url = repo.get("clone_url", "")
    repo_full_name = repo.get("full_name", "")
    ref = payload.get("ref", "")
    commit_sha = payload.get("after", "")

    # Only analyze main/master branch pushes
    if not ref.endswith("/main") and not ref.endswith("/master"):
        return {"message": "Skipping non-main branch push"}

    branch = ref.split("/")[-1]

    job = AnalysisJob(
        repo_url=repo_url,
        branch=branch,
        commit_sha=commit_sha,
        repo_full_name=repo_full_name,
    )

    job_id = f"{repo_full_name}:{commit_sha[:8]}"
    active_jobs[job_id] = job

    background_tasks.add_task(run_analysis, job)

    return {"message": "Analysis queued", "job_id": job_id}


async def handle_pr_event(payload: dict, background_tasks: BackgroundTasks):
    """Handle pull request events."""
    action = payload.get("action", "")

    # Only analyze on open, synchronize, reopened
    if action not in ["opened", "synchronize", "reopened"]:
        return {"message": f"Skipping PR action '{action}'"}

    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})

    repo_url = repo.get("clone_url", "")
    repo_full_name = repo.get("full_name", "")
    pr_number = pr.get("number")
    branch = pr.get("head", {}).get("ref", "main")
    commit_sha = pr.get("head", {}).get("sha", "")

    job = AnalysisJob(
        repo_url=repo_url,
        branch=branch,
        commit_sha=commit_sha,
        pr_number=pr_number,
        repo_full_name=repo_full_name,
    )

    job_id = f"{repo_full_name}:pr-{pr_number}:{commit_sha[:8]}"
    active_jobs[job_id] = job

    background_tasks.add_task(run_analysis, job)

    return {"message": "PR analysis queued", "job_id": job_id}


@app.get("/jobs")
async def list_jobs():
    """List all jobs."""
    return {
        job_id: {
            "status": job.status,
            "repo": job.repo_full_name,
            "pr": job.pr_number,
            "started": job.started_at.isoformat() if job.started_at else None,
            "completed": job.completed_at.isoformat() if job.completed_at else None,
            "error": job.error,
        }
        for job_id, job in active_jobs.items()
    }


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job.status,
        "repo": job.repo_full_name,
        "branch": job.branch,
        "commit": job.commit_sha,
        "pr": job.pr_number,
        "started": job.started_at.isoformat() if job.started_at else None,
        "completed": job.completed_at.isoformat() if job.completed_at else None,
        "error": job.error,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
