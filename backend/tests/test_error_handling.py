from app.core.exceptions import ConflictException, NotFoundException, ValidationException


def test_custom_exception_handler(app, client):
    """Test custom LifeOSException properly serialized into standard error envelope."""
    @app.route("/test-error-endpoint")
    def trigger_error():
        raise ConflictException("Sample conflict occurred", payload={"item": "resource-1"})

    response = client.get("/test-error-endpoint")
    assert response.status_code == 409
    data = response.get_json()
    assert data["success"] is False
    assert data["code"] == "CONFLICT"
    assert "Sample conflict occurred" in data["message"]


def test_405_method_not_allowed(client):
    """Test 405 Method Not Allowed error format."""
    response = client.post("/api/v1/health")
    assert response.status_code == 405
    data = response.get_json()
    assert data["success"] is False
    assert data["code"] == "METHOD_NOT_ALLOWED"

