from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Waste Sorting & Recycling Optimization API", "docs": "/docs"}

def test_create_collector():
    response = client.post(
        "/collectors/",
        json={"username": "ali_barbecha", "full_name": "Ali Tounsi", "phone_number": "12345678"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "ali_barbecha"
    assert data["balance"] == 0.0

def test_duplicate_collector():
    # Attempt to create the same user again
    client.post(
        "/collectors/",
        json={"username": "duplicate_user", "full_name": "Test", "phone_number": "000"}
    )
    response = client.post(
        "/collectors/",
        json={"username": "duplicate_user", "full_name": "Test", "phone_number": "000"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

def test_citizen_search_empty():
    response = client.get("/citizen/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
