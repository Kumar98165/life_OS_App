def test_readiness_probe_success(client):
    """Test readiness check returns 200 when database responds to SELECT 1."""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "ready"
    assert json_data["data"]["database"] == "connected"


def test_structured_request_id_header(client):
    """Test every response contains a traceable X-Request-ID header."""
    response = client.get("/api/v1/ready", headers={"X-Request-ID": "custom-trace-uuid-123"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "custom-trace-uuid-123"

