import pytest

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
