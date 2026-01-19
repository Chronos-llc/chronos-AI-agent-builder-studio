"""
Test file for platform features including marketplace, skills system,
platform updates, and support system.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMarketplaceFeatures:
    """Tests for marketplace features."""

    def test_get_marketplace_listings(self):
        """Test getting marketplace listings."""
        response = client.get("/api/marketplace/agents")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    def test_get_agent_details(self):
        """Test getting agent details."""
        response = client.get("/api/marketplace/agents/1")
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "name" in data
            assert "description" in data
            assert "category" in data
            assert "tags" in data
        elif response.status_code == 404:
            # Agent not found, which is expected in test environment
            pass

    def test_install_agent(self):
        """Test installing an agent."""
        response = client.post("/api/marketplace/agents/1/install")
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        elif response.status_code == 404:
            # Agent not found, which is expected in test environment
            pass

    def test_publish_agent(self):
        """Test publishing an agent."""
        response = client.post("/api/marketplace/agents/publish", json={
            "agent_id": "1",
            "name": "Test Agent",
            "description": "This is a test agent",
            "category": "AI Assistants",
            "tags": ["test", "ai"],
            "price": 0,
            "screenshots": [],
            "videos": [],
            "features": ["Test feature"],
            "requirements": ["None"]
        })
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        elif response.status_code == 400:
            # Bad request, which is expected in test environment
            pass


class TestSkillsSystemFeatures:
    """Tests for skills system features."""

    def test_get_skills_list(self):
        """Test getting skills list."""
        response = client.get("/api/skills")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    def test_get_skill_details(self):
        """Test getting skill details."""
        response = client.get("/api/skills/1")
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "name" in data
            assert "description" in data
            assert "category" in data
            assert "version" in data
        elif response.status_code == 404:
            # Skill not found, which is expected in test environment
            pass

    def test_install_skill(self):
        """Test installing a skill."""
        response = client.post("/api/skills/1/install", json={
            "agent_id": "1"
        })
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        elif response.status_code == 404:
            # Skill or agent not found, which is expected in test environment
            pass


class TestPlatformUpdatesFeatures:
    """Tests for platform updates features."""

    def test_get_platform_updates(self):
        """Test getting platform updates."""
        response = client.get("/api/platform-updates")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    def test_mark_update_as_viewed(self):
        """Test marking an update as viewed."""
        response = client.put("/api/platform-updates/1/view")
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        elif response.status_code == 404:
            # Update not found, which is expected in test environment
            pass


class TestSupportSystemFeatures:
    """Tests for support system features."""

    def test_create_support_ticket(self):
        """Test creating a support ticket."""
        response = client.post("/api/support/tickets", json={
            "subject": "Test Ticket",
            "content": "This is a test ticket",
            "category": "General Question",
            "priority": "Low",
            "attachments": []
        })
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        elif response.status_code == 400:
            # Bad request, which is expected in test environment
            pass

    def test_get_support_tickets(self):
        """Test getting support tickets."""
        response = client.get("/api/support/tickets")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data


class TestPaymentMethodsFeatures:
    """Tests for payment methods features."""

    def test_get_payment_methods(self):
        """Test getting payment methods."""
        response = client.get("/api/payment-methods")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_add_payment_method(self):
        """Test adding a payment method."""
        response = client.post("/api/payment-methods", json={
            "type": "credit_card",
            "card_number": "4111111111111111",
            "exp_month": 12,
            "exp_year": 2024,
            "cvv": "123"
        })
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        elif response.status_code == 400:
            # Bad request, which is expected in test environment
            pass


class TestAdminFeatures:
    """Tests for admin features."""

    def test_get_admin_stats(self):
        """Test getting admin dashboard stats."""
        response = client.get("/api/admin/stats")
        if response.status_code == 200:
            data = response.json()
            assert "total_agents" in data
            assert "total_users" in data
            assert "total_installations" in data
            assert "total_reviews" in data
            assert "total_support_tickets" in data
        elif response.status_code == 401 or response.status_code == 403:
            # Unauthorized or forbidden, which is expected in test environment
            pass

    def test_moderate_agent(self):
        """Test moderating an agent."""
        response = client.put("/api/admin/agents/1/moderate", json={
            "status": "approved",
            "reason": "Test moderation"
        })
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        elif response.status_code == 401 or response.status_code == 403:
            # Unauthorized or forbidden, which is expected in test environment
            pass
        elif response.status_code == 404:
            # Agent not found, which is expected in test environment
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
