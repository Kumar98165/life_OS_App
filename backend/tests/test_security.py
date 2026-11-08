import pytest
from app.core.security import check_resource_ownership
from app.core.exceptions import ForbiddenException, UnauthorizedException


def test_resource_ownership_check_success():
    """Verify ownership check succeeds when IDs match."""
    user_id = "user-uuid-1111"
    check_resource_ownership(resource_user_id=user_id, current_user_id=user_id)


def test_resource_ownership_check_forbidden():
    """Verify ownership check raises ForbiddenException when IDs mismatch."""
    with pytest.raises(ForbiddenException):
        check_resource_ownership(resource_user_id="user-owner-1111", current_user_id="user-attacker-2222")


def test_resource_ownership_check_unauthorized():
    """Verify ownership check raises UnauthorizedException when current user is None."""
    with pytest.raises(UnauthorizedException):
        check_resource_ownership(resource_user_id="user-owner-1111", current_user_id=None)


def test_token_revocation_and_logout(client):
    """Test user logout revokes the refresh token."""
    # Register and login
    register_resp = client.post("/api/v1/auth/register", json={
        "email": "revocation_test@lifeos.io",
        "password": "Password123!",
        "full_name": "Revocation User"
    })
    assert register_resp.status_code == 201
    refresh_token = register_resp.get_json()["data"]["tokens"]["refresh_token"]

    # Logout with refresh token
    logout_resp = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {refresh_token}"})
    assert logout_resp.status_code == 200
    assert logout_resp.get_json()["success"] is True

    # Try to refresh with revoked token -> should be rejected (401)
    refresh_resp = client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert refresh_resp.status_code == 401
    error_data = refresh_resp.get_json()
    assert error_data["success"] is False
    assert error_data["code"] == "TOKEN_REVOKED"

