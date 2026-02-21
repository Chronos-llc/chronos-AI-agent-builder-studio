import inspect

from app.api import integration_moderation, integrations, workflow_generation
from app.models.integration import IntegrationStatus, IntegrationVisibility
from app.models.usage import PlanType, can_publish_integration, has_team_visibility_access
from app.schemas.integration import (
    IntegrationModerationAction,
    IntegrationSubmissionCreate,
    IntegrationVisibility as IntegrationVisibilitySchema,
)


def test_plan_gating_for_publishing():
    assert can_publish_integration(PlanType.FREE) is False
    assert can_publish_integration(PlanType.LITE) is False
    assert can_publish_integration(PlanType.LOTUS) is False
    assert can_publish_integration(PlanType.TEAM_DEVELOPER) is True
    assert can_publish_integration(PlanType.SPECIAL_SERVICE) is True
    assert can_publish_integration(PlanType.ENTERPRISE) is True


def test_team_visibility_access_rule():
    assert has_team_visibility_access(PlanType.FREE) is False
    assert has_team_visibility_access(PlanType.LITE) is False
    assert has_team_visibility_access(PlanType.TEAM_DEVELOPER) is True
    assert has_team_visibility_access(PlanType.SPECIAL_SERVICE) is True
    assert has_team_visibility_access(PlanType.ENTERPRISE) is True


def test_submission_scope_is_limited_to_mcp_and_api():
    assert integrations._is_submission_type_allowed("mcp_server") is True
    assert integrations._is_submission_type_allowed("api") is True
    assert integrations._is_submission_type_allowed("webhook") is False
    assert integrations._is_submission_type_allowed("database") is False


def test_submission_schema_accepts_visibility_and_workflow_flags():
    payload = IntegrationSubmissionCreate(
        name="Research Connector",
        description="Publishes internal research data as tools.",
        integration_type="mcp_server",
        category="automation",
        visibility=IntegrationVisibilitySchema.TEAM,
        config_schema={"command": "npx"},
        credentials_schema={"token": {"required": True, "sensitive": True}},
        supported_features=["query"],
        app_screenshots=[],
        is_workflow_node_enabled=True,
    )
    assert payload.visibility == IntegrationVisibilitySchema.TEAM
    assert payload.is_workflow_node_enabled is True


def test_moderation_actions_cover_required_lifecycle():
    assert IntegrationModerationAction.APPROVE.value == "approve"
    assert IntegrationModerationAction.REJECT.value == "reject"
    assert IntegrationModerationAction.REQUEST_CHANGES.value == "request_changes"


def test_workflow_nodes_endpoint_filters_to_approved_or_published():
    source = inspect.getsource(workflow_generation.list_integration_nodes)
    assert "IntegrationStatus.APPROVED.value" in source
    assert "IntegrationStatus.PUBLISHED.value" in source
    assert "is_workflow_node_enabled == True" in source


def test_install_endpoint_blocks_unpublished_integrations():
    source = inspect.getsource(integrations.create_integration_config)
    assert "Only published integrations can be installed" in source
    assert "integration.status != IntegrationStatus.PUBLISHED.value" in source


def test_moderation_route_requires_manage_marketplace_permission():
    source = inspect.getsource(integration_moderation._require_marketplace_moderation)
    assert "PermissionEnum.MANAGE_MARKETPLACE" in source


def test_integration_visibility_enum_matches_expected_values():
    assert IntegrationVisibility.PRIVATE.value == "private"
    assert IntegrationVisibility.TEAM.value == "team"
    assert IntegrationVisibility.PUBLIC.value == "public"


def test_integration_status_enum_contains_submission_lifecycle():
    statuses = {item.value for item in IntegrationStatus}
    assert {"draft", "submitted", "under_review", "approved", "rejected", "published"}.issubset(statuses)

