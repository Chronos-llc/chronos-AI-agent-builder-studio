"""
Basic test runner for Chronos AI Agent Builder Studio backend
"""
import pytest
import asyncio
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.agent import AgentModel
from app.core.security import get_password_hash


# Test database setup
SQLITE_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLITE_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def setup_database():
    """Set up test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Create test database session"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_user(db):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_agent(db, test_user):
    """Create test agent"""
    agent = AgentModel(
        name="Test Agent",
        description="A test agent for testing",
        system_prompt="You are a helpful test agent.",
        user_prompt_template="{{user_input}}",
        status="draft",
        owner_id=test_user.id
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user"""
    from app.core.security import create_access_token
    
    access_token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {access_token}"}


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Chronos AI Agent Builder Studio API" in response.json()["message"]


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_user_registration(client, db):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "testpassword123",
        "password_confirm": "testpassword123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["username"] == "newuser"


def test_user_login(client, test_user):
    """Test user login"""
    response = client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "testpassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_create_agent(client, auth_headers):
    """Test creating an agent"""
    response = client.post("/api/v1/agents", json={
        "name": "New Test Agent",
        "description": "A new test agent",
        "system_prompt": "You are a helpful assistant.",
        "user_prompt_template": "{{user_input}}",
        "status": "draft"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "New Test Agent"
    assert response.json()["status"] == "draft"


def test_get_agents(client, auth_headers, test_agent):
    """Test getting user's agents"""
    response = client.get("/api/v1/agents", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert any(agent["name"] == test_agent.name for agent in response.json())


def test_get_agent(client, auth_headers, test_agent):
    """Test getting a specific agent"""
    response = client.get(f"/api/v1/agents/{test_agent.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == test_agent.name


def test_update_agent(client, auth_headers, test_agent):
    """Test updating an agent"""
    response = client.put(f"/api/v1/agents/{test_agent.id}", json={
        "description": "Updated test agent description",
        "status": "active"
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["description"] == "Updated test agent description"
    assert response.json()["status"] == "active"


def test_delete_agent(client, auth_headers, test_agent):
    """Test deleting an agent"""
    response = client.delete(f"/api/v1/agents/{test_agent.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Agent deleted successfully"


def test_unauthorized_access(client):
    """Test unauthorized access to protected endpoints"""
    response = client.get("/api/v1/agents")
    assert response.status_code == 401


def test_agent_ownership_verification(client, auth_headers, db, test_user):
    """Test that users can only access their own agents"""
    # Create another user and agent
    other_user = User(
        email="other@example.com",
        username="otheruser",
        full_name="Other User",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_verified=True
    )
    db.add(other_user)
    db.commit()
    
    other_agent = AgentModel(
        name="Other Agent",
        description="Agent belonging to other user",
        system_prompt="You are another agent.",
        owner_id=other_user.id
    )
    db.add(other_agent)
    db.commit()
    
    # Try to access the other user's agent
    response = client.get(f"/api/v1/agents/{other_agent.id}", headers=auth_headers)
    assert response.status_code == 404


if __name__ == "__main__":
    # Run tests manually
    pytest.main([__file__, "-v"])