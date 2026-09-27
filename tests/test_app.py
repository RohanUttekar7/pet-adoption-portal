
import pytest

import database as db
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_add_pet_invalid_name(client):
    response = client.post("/add-pet", data={
        "name": "A",
        "type": "Dog",
        "breed": "Labrador",
        "age": "3",
        "gender": "Male",
        "location": "Pune",
        "description": "Friendly dog",
        "image_url": ""
    })

    assert response.status_code == 200
    assert b"Pet name must be 2-50 characters." in response.data


def test_add_pet_valid(client, monkeypatch):
    calls = {}

    def fake_add_pet(*args):
        calls["args"] = args
        return 999

    monkeypatch.setattr(db, "add_pet", fake_add_pet)

    response = client.post("/add-pet", data={
        "name": "Buddy",
        "type": "Dog",
        "breed": "Labrador",
        "age": "3",
        "gender": "Male",
        "location": "Pune",
        "description": "Friendly dog",
        "image_url": ""
    })

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/pets")
    assert calls["args"][0] == "Buddy"


def test_pets_api_returns_json(client):
    response = client.get("/api/pets")

    assert response.status_code == 200
    assert response.is_json
    assert isinstance(response.get_json(), list)


def test_adoptions_api_returns_json(client):
    response = client.get("/api/adoptions")

    assert response.status_code == 200
    assert response.is_json
    assert isinstance(response.get_json(), list)
