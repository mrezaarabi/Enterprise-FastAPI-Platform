import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


def test_get_users(client: TestClient, superuser_token_headers: dict):
    """Test getting all users as a superuser"""
    response = client.get("/api/v1/users/", headers=superuser_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_users_not_allowed(client: TestClient, normal_user_token_headers: dict):
    """Test that normal users can't get all users"""
    response = client.get("/api/v1/users/", headers=normal_user_token_headers)
    assert response.status_code == 403


def test_create_user(client: TestClient, superuser_token_headers: dict):
    """Test creating a new user as superuser"""
    data = {
        "email": "newuser@example.com",
        "password": "NewUser123!",
        "full_name": "New User",
        "is_active": True,
        "is_superuser": False
    }
    response = client.post(
        "/api/v1/users/", 
        json=data,
        headers=superuser_token_headers
    )
    assert response.status_code == 201
    created_user = response.json()
    assert created_user["email"] == data["email"]
    assert created_user["full_name"] == data["full_name"]
    assert "password" not in created_user  # Password shouldn't be returned


def test_get_user_me(client: TestClient, normal_user_token_headers: dict):
    """Test getting the current user information"""
    response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    assert response.status_code == 200
    current_user = response.json()
    assert current_user["email"] == "user@example.com"
    assert current_user["is_active"] is True


def test_update_user_me(client: TestClient, normal_user_token_headers: dict):
    """Test updating own user information"""
    data = {
        "full_name": "Updated User Name"
    }
    response = client.put(
        "/api/v1/users/me", 
        json=data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["full_name"] == data["full_name"]


def test_get_specific_user(
    client: TestClient, 
    normal_user_token_headers: dict,
    db: Session
):
    """Test getting a specific user by ID"""
    # Get the user ID first
    response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    current_user = response.json()
    user_id = current_user["id"]
    
    # Now get the user by ID
    response = client.get(
        f"/api/v1/users/{user_id}", 
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id


def test_delete_user(
    client: TestClient, 
    superuser_token_headers: dict,
    db: Session
):
    """Test deleting a user as superuser"""
    # Create a user to delete
    data = {
        "email": "todelete@example.com",
        "password": "Delete123!",
        "full_name": "To Delete",
        "is_active": True,
        "is_superuser": False
    }
    create_response = client.post(
        "/api/v1/users/", 
        json=data,
        headers=superuser_token_headers
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    
    # Now delete the user
    delete_response = client.delete(
        f"/api/v1/users/{user_id}", 
        headers=superuser_token_headers
    )
    assert delete_response.status_code == 204
    
    # Verify the user is gone
    get_response = client.get(
        f"/api/v1/users/{user_id}", 
        headers=superuser_token_headers
    )
    assert get_response.status_code == 404