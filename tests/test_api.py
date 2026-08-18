import pytest

from fastapi.testclient import TestClient

import api.main as api_main


class FakeModel:

    def predict(self, input_data):

        return [
            1234567.89
        ]


@pytest.fixture
def client(monkeypatch):

    monkeypatch.setattr(
        api_main.mlflow.sklearn,
        "load_model",
        lambda model_uri: FakeModel(),
    )

    with TestClient(api_main.app) as test_client:

        yield test_client
        
# les tests


def test_health(client):

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert (
        data["model"]
        ==
        "models:/HousePriceModel@champion"
    )


def test_predict_valid_house(client):

    response = client.post(
        "/predict",
        json={
            "surface": 100.0,
            "rooms": 3,
            "age": 5,
            "distance_city": 4.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["predicted_price"] == pytest.approx(
        1234567.89
    )

    assert (
        data["model"]
        ==
        "HousePriceModel@champion"
    )


def test_predict_negative_surface(client):

    response = client.post(
        "/predict",
        json={
            "surface": -100.0,
            "rooms": 3,
            "age": 5,
            "distance_city": 4.0,
        },
    )

    assert response.status_code == 422


def test_predict_zero_rooms(client):

    response = client.post(
        "/predict",
        json={
            "surface": 100.0,
            "rooms": 0,
            "age": 5,
            "distance_city": 4.0,
        },
    )

    assert response.status_code == 422


def test_predict_negative_age(client):

    response = client.post(
        "/predict",
        json={
            "surface": 100.0,
            "rooms": 3,
            "age": -1,
            "distance_city": 4.0,
        },
    )

    assert response.status_code == 422


def test_predict_missing_field(client):

    response = client.post(
        "/predict",
        json={
            "surface": 100.0,
            "rooms": 3,
            "age": 5,
        },
    )

    assert response.status_code == 422