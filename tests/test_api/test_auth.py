from fastapi.testclient import TestClient
import pytest

def test_login(client: TestClient, normal_user_token_headers):
    """Test logging in with correct credentials"""
    login_data = {
        "username": "user@example.com",
        "password": "User123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient):
    """Test logging in with incorrect password"""
    login_data = {
        "username": "user@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401


def test_register_new_user(client: TestClient):
    """Test registering a new user"""
    user_data = {
        "email": "register@example.com",
        "password": "Register123!",
        "full_name": "Register User"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_register_existing_user(client: TestClient, normal_user_token_headers):
    """Test that registering an existing user fails"""
    user_data = {
        "email": "user@example.com",  # This email already exists
        "password": "Password123!",
        "full_name": "Duplicate User"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400