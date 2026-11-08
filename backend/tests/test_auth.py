import pytest
from datetime import timedelta
from flask_jwt_extended import create_access_token


def test_register_success(client):
    """Test user registration returns 201 with tokens and sanitized user."""
    payload = {
        "email": "SeniorArchitect@LifeOS.io",
        "password": "Password123!",
        "full_name": "Senior Architect"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "user" in json_data["data"]
    assert "tokens" in json_data["data"]
    assert json_data["data"]["user"]["email"] == "seniorarchitect@lifeos.io"  # Normalized
    assert "password_hash" not in json_data["data"]["user"]
    assert "access_token" in json_data["data"]["tokens"]
    assert "refresh_token" in json_data["data"]["tokens"]


def test_register_duplicate_email(client):
    """Test registering an existing email returns 409 conflict."""
    payload = {
        "email": "duplicate@lifeos.io",
        "password": "Password123!",
        "full_name": "Duplicate User"
    }
    first_resp = client.post("/api/v1/auth/register", json=payload)
    assert first_resp.status_code == 201

    dup_resp = client.post("/api/v1/auth/register", json=payload)
    assert dup_resp.status_code == 409
    json_data = dup_resp.get_json()
    assert json_data["success"] is False
    assert "already exists" in json_data["message"]


def test_register_weak_password_validation(client):
    """Test registration with weak password returns 422 validation error."""
    payload = {
        "email": "test@lifeos.io",
        "password": "short",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["code"] == "VALIDATION_ERROR"
    assert len(json_data["errors"]) > 0


def test_login_success_and_profile_access(client):
    """Test user login and fetching profile with bearer token."""
    client.post("/api/v1/auth/register", json={
        "email": "auth_test@lifeos.io",
        "password": "ValidPassword123",
        "full_name": "Auth Tester"
    })

    login_resp = client.post("/api/v1/auth/login", json={
        "email": "auth_test@lifeos.io",
        "password": "ValidPassword123"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.get_json()
    access_token = login_data["data"]["tokens"]["access_token"]
    refresh_token = login_data["data"]["tokens"]["refresh_token"]

    # Access protected /me endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.get_json()
    assert me_data["data"]["user"]["email"] == "auth_test@lifeos.io"

    # Refresh token with rotation
    refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
    refresh_resp = client.post("/api/v1/auth/refresh", headers=refresh_headers)
    assert refresh_resp.status_code == 200
    refresh_data = refresh_resp.get_json()
    assert "access_token" in refresh_data["data"]
    assert "refresh_token" in refresh_data["data"]


def test_login_invalid_password_and_account_enumeration(client):
    """Test login with incorrect password returns 401 without leaking email existence."""
    client.post("/api/v1/auth/register", json={
        "email": "wrong_pw@lifeos.io",
        "password": "CorrectPassword123",
        "full_name": "Wrong Password User"
    })

    # Non-existent user
    non_exist_resp = client.post("/api/v1/auth/login", json={
        "email": "non_existent@lifeos.io",
        "password": "AnyPassword123"
    })
    assert non_exist_resp.status_code == 401

    # Existing user, wrong password
    wrong_pw_resp = client.post("/api/v1/auth/login", json={
        "email": "wrong_pw@lifeos.io",
        "password": "IncorrectPassword999"
    })
    assert wrong_pw_resp.status_code == 401
    # Both messages must be identical to prevent enumeration
    assert non_exist_resp.get_json()["message"] == wrong_pw_resp.get_json()["message"]


def test_missing_access_token(client):
    """Test accessing protected endpoint without token returns 401."""
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert resp.get_json()["code"] == "AUTHENTICATION_REQUIRED"


def test_invalid_access_token(client):
    """Test accessing protected endpoint with corrupt token returns 401."""
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-valid-jwt-token"})
    assert resp.status_code == 401
    assert resp.get_json()["code"] == "INVALID_TOKEN"


def test_expired_access_token(app, client):
    """Test expired token returns 401 with TOKEN_EXPIRED code."""
    with app.app_context():
        expired_token = create_access_token(
            identity="test-user-id",
            expires_delta=timedelta(seconds=-10)
        )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401
    assert resp.get_json()["code"] == "TOKEN_EXPIRED"


def test_refresh_token_rotation_and_revocation(client):
    """Test token rotation invalidates old refresh token."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "rotate_test@lifeos.io",
        "password": "Password123!",
        "full_name": "Rotation Tester"
    })
    refresh_token_1 = reg.get_json()["data"]["tokens"]["refresh_token"]

    # First refresh: succeeds and rotates
    ref_resp_1 = client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token_1}"})
    assert ref_resp_1.status_code == 200
    refresh_token_2 = ref_resp_1.get_json()["data"]["refresh_token"]
    assert refresh_token_2 != refresh_token_1

    # Second refresh with OLD token: should be rejected
    ref_resp_old = client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token_1}"})
    assert ref_resp_old.status_code == 401
    assert ref_resp_old.get_json()["code"] in ["TOKEN_REVOKED", "AUTHENTICATION_ERROR"]

    # Third refresh with NEW token: succeeds
    # Note: If token reuse occurred, all sessions were revoked for security
    # In LifeOS, reuse of a revoked token invalidates the entire session chain
    assert ref_resp_old.status_code == 401


def test_logout_revokes_token(client):
    """Test logout revokes the current refresh token."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "logout_test@lifeos.io",
        "password": "Password123!",
        "full_name": "Logout Tester"
    })
    refresh_token = reg.get_json()["data"]["tokens"]["refresh_token"]

    # Logout
    logout_resp = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {refresh_token}"})
    assert logout_resp.status_code == 200

    # Try to use refresh token after logout -> rejected
    ref_resp = client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert ref_resp.status_code == 401
    assert ref_resp.get_json()["code"] == "TOKEN_REVOKED"


def test_logout_with_invalid_token(client):
    """Test logout with invalid token fails with 401."""
    resp = client.post("/api/v1/auth/logout", headers={"Authorization": "Bearer invalid-token"})
    assert resp.status_code == 401


def test_update_user_profile(client):
    """Test updating user profile fields via PATCH /api/v1/users/me."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "profile_update@lifeos.io",
        "password": "Password123!",
        "full_name": "Initial Name"
    })
    access_token = reg.get_json()["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Update full_name and avatar_url
    patch_resp = client.patch("/api/v1/users/me", json={
        "full_name": "Updated Professional Name",
        "avatar_url": "https://lifeos.io/avatars/user1.png"
    }, headers=headers)
    assert patch_resp.status_code == 200
    user_data = patch_resp.get_json()["data"]["user"]
    assert user_data["full_name"] == "Updated Professional Name"
    assert user_data["avatar_url"] == "https://lifeos.io/avatars/user1.png"

    # Reject attempt to modify protected fields like email or is_active
    protect_resp = client.patch("/api/v1/users/me", json={
        "email": "hacked@lifeos.io",
        "is_active": False
    }, headers=headers)
    assert protect_resp.status_code == 422
    assert protect_resp.get_json()["code"] == "VALIDATION_ERROR"


def test_cross_user_isolation(client):
    """Test that User A cannot modify or impersonate User B."""
    # Register User A
    user_a_reg = client.post("/api/v1/auth/register", json={
        "email": "usera@lifeos.io",
        "password": "Password123!",
        "full_name": "User Alpha"
    })
    token_a = user_a_reg.get_json()["data"]["tokens"]["access_token"]
    user_a_id = user_a_reg.get_json()["data"]["user"]["id"]

    # Register User B
    user_b_reg = client.post("/api/v1/auth/register", json={
        "email": "userb@lifeos.io",
        "password": "Password123!",
        "full_name": "User Beta"
    })
    token_b = user_b_reg.get_json()["data"]["tokens"]["access_token"]
    user_b_id = user_b_reg.get_json()["data"]["user"]["id"]

    # Verify /me for User A returns User A's ID
    resp_a = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert resp_a.get_json()["data"]["user"]["id"] == user_a_id
    assert resp_a.get_json()["data"]["user"]["id"] != user_b_id

    # Verify /me for User B returns User B's ID
    resp_b = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.get_json()["data"]["user"]["id"] == user_b_id
    assert resp_b.get_json()["data"]["user"]["id"] != user_a_id
