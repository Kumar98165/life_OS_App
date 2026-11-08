def test_health_check_endpoint(client):
    """Test health check endpoint returns 200 and standard envelope."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["status"] == "success"
    assert json_data["message"] == "Service is operational"
    assert json_data["data"]["status"] == "healthy"
    assert json_data["data"]["service"] == "LifeOS Backend API"


def test_404_not_found(client):
    """Test standard 404 error envelope."""
    response = client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["status"] == "error"
    assert json_data["code"] == "NOT_FOUND"
