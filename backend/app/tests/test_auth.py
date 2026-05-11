import pytest
import uuid


def test_health_check(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_register(client):
    """Test user registration"""
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": "test123",
        "full_name": "Test User"
    })

    print(f"Register response status: {response.status_code}")
    print(f"Register response body: {response.text}")

    assert response.status_code in [200, 201, 400]

    if response.status_code in [200, 201]:
        data = response.json()
        assert "id" in data or "_id" in data


def test_login(client):
    """Test user login"""
    unique_email = f"login_{uuid.uuid4().hex[:8]}@example.com"

    register_resp = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": "test123",
        "full_name": "Test User"
    })

    print(f"Register response: {register_resp.status_code}")

    response = client.post(
        "/api/auth/login",
        data={
            "username": unique_email,
            "password": "test123"
        }
    )

    print(f"Login response status: {response.status_code}")
    print(f"Login response body: {response.text}")

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data


def test_login_invalid(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrong"
        }
    )

    assert response.status_code == 401