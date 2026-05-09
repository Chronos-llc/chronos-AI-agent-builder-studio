from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class WorkflowJobStep(BaseModel):
    """Individual step in a GitHub Actions workflow job."""
    name: str = Field(..., description="Name of the step")
    status: str = Field(..., description="Current status of the step")
    conclusion: Optional[str] = Field(None, description="Conclusion of the step (success, failure, etc.)")
    number: int = Field(..., description="Step number in the job")
    started_at: Optional[datetime] = Field(None, description="When the step started (ISO 8601)")
    completed_at: Optional[datetime] = Field(None, description="When the step completed (ISO 8601)")


class WorkflowJob(BaseModel):
    """GitHub Actions workflow job object."""
    id: int = Field(..., description="Unique identifier of the job")
    run_id: int = Field(..., description="ID of the workflow run")
    workflow_name: str = Field(..., description="Name of the workflow")
    head_branch: str = Field(..., description="Branch that triggered the workflow")
    run_url: str = Field(..., description="API URL for the workflow run")
    run_attempt: int = Field(..., description="Attempt number for this workflow run")
    node_id: str = Field(..., description="Global node ID of the job")
    head_sha: str = Field(..., description="Commit SHA that triggered the workflow")
    url: str = Field(..., description="API URL for the job")
    html_url: str = Field(..., description="GitHub URL for the job")
    status: str = Field(..., description="Current status of the job")
    conclusion: Optional[str] = Field(None, description="Conclusion of the job (success, failure, etc.)")
    created_at: datetime = Field(..., description="When the job was created (ISO 8601)")
    started_at: datetime = Field(..., description="When the job started (ISO 8601)")
    completed_at: datetime = Field(..., description="When the job completed (ISO 8601)")
    name: str = Field(..., description="Display name of the job")
    steps: List[WorkflowJobStep] = Field(default_factory=list, description="Steps in the job")
    check_run_url: Optional[str] = Field(None, description="URL of the associated check run")
    labels: List[str] = Field(default_factory=list, description="Labels applied to the job")
    runner_id: int = Field(..., description="ID of the runner that executed the job")
    runner_name: str = Field(..., description="Name of the runner")
    runner_group_id: int = Field(..., description="ID of the runner group")
    runner_group_name: str = Field(..., description="Name of the runner group")


class GitHubRepository(BaseModel):
    """Simplified GitHub repository object for webhook payloads."""
    id: int = Field(..., description="Repository ID")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full repository name (owner/name)")
    owner: Dict[str, Any] = Field(..., description="Repository owner information")
    private: bool = Field(..., description="Whether the repository is private")
    html_url: str = Field(..., description="GitHub URL for the repository")
    description: Optional[str] = Field(None, description="Repository description")
    fork: bool = Field(..., description="Whether the repository is a fork")
    url: str = Field(..., description="API URL for the repository")
    created_at: datetime = Field(..., description="When the repository was created (ISO 8601)")
    updated_at: datetime = Field(..., description="When the repository was last updated (ISO 8601)")
    pushed_at: Optional[datetime] = Field(None, description="When the repository was last pushed to (ISO 8601)")


class GitHubUser(BaseModel):
    """Simplified GitHub user/bot object for webhook payloads."""
    id: int = Field(..., description="User ID")
    login: str = Field(..., description="Username")
    type: str = Field(..., description="Type of user (User or Bot)")
    site_admin: bool = Field(..., description="Whether the user is a site administrator")
    html_url: str = Field(..., description="GitHub URL for the user")
    avatar_url: Optional[str] = Field(None, description="URL of the user's avatar")


class GitHubOrganization(BaseModel):
    """Simplified GitHub organization object for webhook payloads."""
    id: int = Field(..., description="Organization ID")
    login: str = Field(..., description="Organization login")
    type: str = Field(default="Organization", description="Type of entity (always Organization)")
    html_url: str = Field(..., description="GitHub URL for the organization")
    avatar_url: Optional[str] = Field(None, description="URL of the organization's avatar")


class GitHubWorkflowJobWebhookPayload(BaseModel):
    """Top-level payload for GitHub Actions workflow_job webhook events."""
    action: str = Field(..., description="Action that was performed (queued, in_progress, completed)")
    workflow_job: WorkflowJob = Field(..., description="The workflow job object")
    repository: GitHubRepository = Field(..., description="Repository where the event occurred")
    organization: Optional[GitHubOrganization] = Field(None, description="Organization if applicable")
    sender: GitHubUser = Field(..., description="User or bot that triggered the event")


class GitHubWebhookEvent(BaseModel):
    """Wrapper for GitHub webhook events including headers and payload."""
    event_type: str = Field(..., description="Value of X-GitHub-Event header (e.g., 'workflow_job')")
    payload: GitHubWorkflowJobWebhookPayload = Field(..., description="Parsed webhook payload")
    signature: Optional[str] = Field(None, description="Value of X-Hub-Signature-256 header for verification")
    delivery_id: Optional[str] = Field(None, description="Value of X-GitHub-Delivery header")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "workflow_job",
                "payload": {
                    "action": "completed",
                    "workflow_job": {
                        "id": 75146993790,
                        "run_id": 25597945707,
                        "workflow_name": "Scheduled",
                        "head_branch": "main",
                        "run_url": "https://api.github.com/repos/Chronos-llc/chronos-AI-agent-builder-studio/actions/runs/25597945707",
                        "run_attempt": 1,
                        "node_id": "CR_kwDORElxzc8AAAARfxwgfg",
                        "head_sha": "618c5356adf108a90768d3c425fb932a98387b9f",
                        "url": "https://api.github.com/repos/Chronos-llc/chronos-AI-agent-builder-studio/actions/jobs/75146993790",
                        "html_url": "https://github.com/Chronos-llc/chronos-AI-agent-builder-studio/actions/runs/25597945707/job/75146993790",
                        "status": "completed",
                        "conclusion": "success",
                        "created_at": "2026-05-09T09:41:15Z",
                        "started_at": "2026-05-09T09:41:17Z",
                        "completed_at": "2026-05-09T09:42:51Z",
                        "name": "Analyze (javascript-typescript)",
                        "steps": [
                            {
                                "name": "Set up job",
                                "status": "completed",
                                "conclusion": "success",
                                "number": 1,
                                "started_at": "2026-05-09T09:41:17Z",
                                "completed_at": "2026-05-09T09:41:18Z"
                            }
                        ],
                        "check_run_url": "https://api.github.com/repos/Chronos-llc/chronos-AI-agent-builder-studio/check-runs/123456789",
                        "labels": ["ubuntu-latest"],
                        "runner_id": 1000000125,
                        "runner_name": "GitHub Actions 1000000125",
                        "runner_group_id": 0,
                        "runner_group_name": "GitHub Actions"
                    },
                    "repository": {
                        "id": 123456789,
                        "name": "chronos-AI-agent-builder-studio",
                        "full_name": "Chronos-llc/chronos-AI-agent-builder-studio",
                        "owner": {
                            "login": "Chronos-llc",
                            "id": 987654321,
                            "type": "Organization",
                            "site_admin": False
                        },
                        "private": False,
                        "html_url": "https://github.com/Chronos-llc/chronos-AI-agent-builder-studio",
                        "description": "AI Agent Builder Studio",
                        "fork": False,
                        "url": "https://api.github.com/repos/Chronos-llc/chronos-AI-agent-builder-studio",
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2026-05-09T09:40:00Z",
                        "pushed_at": "2026-05-09T09:42:00Z"
                    },
                    "organization": {
                        "id": 987654321,
                        "login": "Chronos-llc",
                        "type": "Organization",
                        "html_url": "https://github.com/Chronos-llc",
                        "avatar_url": "https://avatars.githubusercontent.com/u/987654321?v=4"
                    },
                    "sender": {
                        "id": 12345678,
                        "login": "github-actions[bot]",
                        "type": "Bot",
                        "site_admin": False,
                        "html_url": "https://github.com/github-actions[bot]",
                        "avatar_url": "https://avatars.githubusercontent.com/u/12345678?v=4"
                    }
                },
                "signature": "sha256=abc123def456...",
                "delivery_id": "12345-67890-abcde-fghij"
            }
        }