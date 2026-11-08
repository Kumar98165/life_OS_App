import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Create and configure a testing Flask app instance."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test HTTP client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Register and log in a default test user, returning Bearer auth headers."""
    reg_payload = {
        "email": "architect@lifeos.internal",
        "password": "Password123!",
        "full_name": "Lead Architect"
    }
    resp = client.post("/api/v1/auth/register", json=reg_payload)
    token = resp.get_json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


