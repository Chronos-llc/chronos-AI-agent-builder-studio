"""Enhanced MCP lightweight tests."""

from app.core.phone_providers import PhoneProviderManager
from app.schemas.mcp_server import MCPServerCreate, MCPServerUpdate


def test_mcp_server_create_schema_defaults():
    payload = MCPServerCreate(
        name="Test MCP",
        server_url="http://localhost:8080",
    )
    assert payload.timeout == 30
    assert payload.weight == 1
    assert payload.max_connections == 10


def test_mcp_server_update_schema_accepts_partial():
    payload = MCPServerUpdate(name="Updated MCP", is_active=True)
    assert payload.name == "Updated MCP"
    assert payload.is_active is True


def test_phone_provider_manager_availability_shape():
    manager = PhoneProviderManager()
    availability = manager.availability()
    assert isinstance(availability, list)
    assert all("provider" in item for item in availability)
    assert all("configured" in item for item in availability)

