from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DependabotAlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DependabotAlertState(str, Enum):
    OPEN = "open"
    DISMISSED = "dismissed"
    FIXED = "fixed"


class DependabotAlertAction(str, Enum):
    CREATE = "create"
    DISMISS = "dismiss"
    REOPEN = "reopen"
    RESOLVE = "resolve"
    UPDATE = "update"


class DependabotAlertOwner(BaseModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    user_view_type: str
    site_admin: bool


class DependabotAlertRepository(BaseModel):
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: DependabotAlertOwner
    html_url: str
    description: Optional[str] = None
    fork: bool
    url: str
    forks_url: str
    keys_url: str
    collaborators_url: str
    teams_url: str
    hooks_url: str
    issue_events_url: str
    events_url: str
    assignees_url: str
    branches_url: str
    tags_url: str
    blobs_url: str
    git_tags_url: str
    git_refs_url: str
    trees_url: str
    statuses_url: str
    languages_url: str
    stargazers_url: str
    contributors_url: str
    subscribers_url: str
    subscription_url: str
    commits_url: str
    git_commits_url: str
    comments_url: str
    issue_comment_url: str
    contents_url: str
    compare_url: str
    merges_url: str
    archive_url: str
    downloads_url: str
    issues_url: str
    pulls_url: str
    milestones_url: str
    notifications_url: str
    labels_url: str
    releases_url: str
    deployments_url: str
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    git_url: str
    ssh_url: str
    clone_url: str
    svn_url: str
    homepage: Optional[str] = None
    size: int
    stargazers_count: int
    watchers_count: int
    language: Optional[str] = None
    has_issues: bool
    has_projects: bool
    has_downloads: bool
    has_wiki: bool
    has_pages: bool
    has_discussions: bool
    forks_count: int
    mirror_url: Optional[str] = None
    archived: bool
    disabled: bool
    open_issues_count: int
    license: Optional[Dict[str, Any]] = None
    allow_forking: bool
    is_template: bool
    web_commit_signoff_required: bool
    has_pull_requests: bool
    pull_request_creation_policy: str
    topics: List[str] = []
    visibility: str
    forks: int
    open_issues: int
    watchers: int
    default_branch: str
    custom_properties: Dict[str, Any] = {}


class DependabotAlertWebhook(BaseModel):
    action: DependabotAlertAction
    alert: Dict[str, Any] = Field(..., description="The full alert object from GitHub")
    repository: DependabotAlertRepository
    organization: Optional[DependabotAlertOwner] = None
    sender: DependabotAlertOwner


class DependabotAlertCreate(BaseModel):
    """Schema for storing a Dependabot alert in the database."""
    github_alert_id: int = Field(..., description="GitHub's unique alert ID")
    alert_number: int
    node_id: str
    affected_package_name: str
    affected_range: Optional[str] = None
    external_reference: Optional[str] = None
    external_identifier: Optional[str] = None
    ghsa_id: Optional[str] = None
    severity: DependabotAlertSeverity
    state: DependabotAlertState = DependabotAlertState.OPEN
    action: DependabotAlertAction
    fixed_in: Optional[str] = None
    created_at: Optional[datetime] = None


class DependabotAlertResponse(DependabotAlertCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DependabotAlertListResponse(BaseModel):
    total: int
    alerts: List[DependabotAlertResponse]


class DependabotAlertWebhookResponse(BaseModel):
    success: bool
    message: str
    alert_id: Optional[int] = None