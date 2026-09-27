
import uuid

import pytest
from werkzeug.security import generate_password_hash

import database as db
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def login_test_user(client):
    """Log in a test user."""
    with client.session_transaction() as session:
        session["user_id"] = 1


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_register(client):
    email = f"test-{uuid.uuid4().hex}@example.com"
    response = client.post(
        "/register",
        data={
            "name": "Test User",
            "email": email,
            "password": "testpassword123",
            "confirm_password": "testpassword123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account created successfully!" in response.data


def test_login(client):
    email = f"login-{uuid.uuid4().hex}@example.com"
    password = "testpassword123"
    db.create_user(
        "Login Tester",
        email,
        generate_password_hash(password),
    )

    response = client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"You are now logged in." in response.data


def test_add_pet_requires_login(client):
    response = client.get("/add-pet")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_add_pet_invalid_name(client):
    login_test_user(client)
    response = client.post(
        "/add-pet",
        data={
            "name": "A",
            "type": "Dog",
            "breed": "Labrador",
            "age": "3",
            "gender": "Male",
            "location": "Pune",
            "description": "Friendly dog",
            "image_url": "",
        },
    )
    assert response.status_code == 200
    assert b"Pet name must be 2-50 characters." in response.data


def test_add_pet_valid(client, monkeypatch):
    login_test_user(client)
    calls = {}

    def fake_add_pet(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return 999

    monkeypatch.setattr(db, "add_pet", fake_add_pet)
    response = client.post(
        "/add-pet",
        data={
            "name": "Buddy",
            "type": "Dog",
            "breed": "Labrador",
            "age": "3",
            "gender": "Male",
            "location": "Pune",
            "description": "Friendly dog",
            "image_url": "",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    assert calls["args"][0] == "Buddy"
    assert calls["kwargs"]["owner_id"] == 1


def test_pets_api_returns_json(client):
    response = client.get("/api/pets")
    assert response.status_code == 200
    assert response.is_json
    assert isinstance(response.get_json(), list)


def test_adoptions_api_returns_json(client):
    login_test_user(client)
    response = client.get("/api/adoptions")
    assert response.status_code == 200
    assert response.is_json
    assert isinstance(response.get_json(), list)


def test_logout(client):
    login_test_user(client)
    response = client.post("/logout")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
