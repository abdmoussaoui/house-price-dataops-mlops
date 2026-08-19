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
    
# ajouté
def test_metrics(client):

    # Etat initial des metriques
    before = client.get("/metrics")

    assert before.status_code == 200

    before_data = before.json()

    # Requete valide
    response_health = client.get("/health")

    assert response_health.status_code == 200

    # Requete volontairement invalide -> 422
    response_invalid = client.post(
        "/predict",
        json={
            "surface": -100.0,
            "rooms": 3,
            "age": 5,
            "distance_city": 4.0,
        },
    )

    assert response_invalid.status_code == 422

    # Etat apres les deux requetes
    after = client.get("/metrics")

    assert after.status_code == 200

    data = after.json()

    assert data["service"] == "mini-house-api"

    assert data["model"] == "HousePriceModel@champion"

    assert (
        data["total_requests"]
        == before_data["total_requests"] + 2
    )

    assert (
        data["successful_requests"]
        == before_data["successful_requests"] + 1
    )

    assert (
        data["client_errors"]
        == before_data["client_errors"] + 1
    )

    assert data["server_errors"] >= 0

    assert data["last_response_time_ms"] >= 0

    assert data["average_response_time_ms"] >= 0
# fin


# ajouté
class FakeModelVersion:

    version = "1"
    run_id = "fake-run-id"


class FakeRunData:

    metrics = {
        "train_mae": 10000.0,
        "train_rmse": 13000.0,
        "train_r2": 0.99,
        "test_mae": 47000.0,
        "test_rmse": 58000.0,
        "test_r2": 0.98,
        "baseline_mae": 562500.0,
    }


class FakeRun:

    data = FakeRunData()


class FakeMlflowClient:

    def get_model_version_by_alias(
        self,
        name,
        alias,
    ):

        return FakeModelVersion()

    def get_run(
        self,
        run_id,
    ):

        return FakeRun()
# fin

# ajouté
def test_ml_metrics(
    client,
    monkeypatch,
):

    monkeypatch.setattr(
        api_main,
        "MlflowClient",
        FakeMlflowClient,
    )

    response = client.get(
        "/ml-metrics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["model"] == "HousePriceModel"

    assert data["alias"] == "champion"

    assert data["version"] == "1"

    assert data["run_id"] == "fake-run-id"

    assert data["train_mae"] == 10000.0

    assert data["test_mae"] == 47000.0

    assert data["test_rmse"] == 58000.0

    assert data["test_r2"] == 0.98

    assert data["baseline_mae"] == 562500.0
# fin

# ajoiuté
def test_drift_detection(
    client,
    monkeypatch,
):

    # Etat de production propre pour ce test
    fresh_monitoring = {
        "prediction_count": 0,
        "feature_sums": {
            "surface": 0.0,
            "rooms": 0.0,
            "age": 0.0,
            "distance_city": 0.0,
        },
    }

    monkeypatch.setattr(
        api_main,
        "production_monitoring",
        fresh_monitoring,
    )

    # ---------------------------------
    # 1. Aucune prediction
    # ---------------------------------

    response = client.get(
        "/drift"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["status"]
        == "waiting_for_predictions"
    )

    assert data["prediction_count"] == 0

    assert data["overall_drift"] is False

    # ---------------------------------
    # 2. Donnees proches de la reference
    # ---------------------------------

    response_1 = client.post(
        "/predict",
        json={
            "surface": 105.5,
            "rooms": 3,
            "age": 6,
            "distance_city": 4.86,
        },
    )

    response_2 = client.post(
        "/predict",
        json={
            "surface": 105.5,
            "rooms": 4,
            "age": 6,
            "distance_city": 4.86,
        },
    )

    assert response_1.status_code == 200
    assert response_2.status_code == 200

    response = client.get(
        "/drift"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["prediction_count"] == 2

    assert data["overall_drift"] is False

    # ---------------------------------
    # 3. Reinitialiser pour simuler
    #    un autre flux de production
    # ---------------------------------

    fresh_monitoring[
        "prediction_count"
    ] = 0

    for feature in fresh_monitoring[
        "feature_sums"
    ]:

        fresh_monitoring[
            "feature_sums"
        ][feature] = 0.0

    # ---------------------------------
    # 4. Donnees volontairement eloignees
    # ---------------------------------

    response = client.post(
        "/predict",
        json={
            "surface": 200.0,
            "rooms": 6,
            "age": 18,
            "distance_city": 9.0,
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/drift"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["prediction_count"] == 1

    assert data["overall_drift"] is True

    assert (
        data["features"]["surface"][
            "drift_detected"
        ]
        is True
    )
# fin