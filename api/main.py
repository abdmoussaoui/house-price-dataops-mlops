import os
import time
import json
from pathlib import Path
from contextlib import asynccontextmanager

import mlflow
from mlflow import MlflowClient
import mlflow.sklearn
import pandas as pd

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field


# TRACKING_URI = "http://127.0.0.1:5000"

TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)


MODEL_NAME = "HousePriceModel"

MODEL_ALIAS = "champion"

# ajouté
REFERENCE_STATS_PATH = (
    Path(__file__).resolve().parent
    / "reference_stats.json"
)


with open(
    REFERENCE_STATS_PATH,
    "r",
    encoding="utf-8",
) as file:

    reference_stats = json.load(file)


DRIFT_THRESHOLD_PERCENT = 20.0
# fin

MODEL_URI = (
    f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
)


mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_registry_uri(TRACKING_URI)


model = None


class HouseInput(BaseModel):
    surface: float = Field(gt=0)
    rooms: int = Field(gt=0)
    age: int = Field(ge=0)
    distance_city: float = Field(ge=0)


class PredictionResponse(BaseModel):
    predicted_price: float
    model: str


@asynccontextmanager
async def lifespan(app: FastAPI):

    global model

    print(
        f"Chargement du modèle : {MODEL_URI}"
    )

    model = mlflow.sklearn.load_model(
        MODEL_URI
    )

    print("Modèle chargé avec succès.")

    yield

    print("Arrêt de l'API.")


app = FastAPI(
    title="House Price Prediction API",
    description=(
        "API de prédiction du prix "
        "d'un logement."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ajoute 
monitoring = {
    "total_requests": 0,
    "successful_requests": 0,
    "client_errors": 0,
    "server_errors": 0,
    "total_response_time_ms": 0.0,
    "last_response_time_ms": 0.0,
}

# ajouté
production_monitoring = {
    "prediction_count": 0,
    "feature_sums": {
        "surface": 0.0,
        "rooms": 0.0,
        "age": 0.0,
        "distance_city": 0.0,
    },
}
# fin


@app.middleware("http")
async def monitor_requests(
    request: Request,
    call_next,
):

    # On évite que /metrics modifie ses propres métriques
    if request.url.path == "/metrics":
        return await call_next(request)

    start_time = time.perf_counter()

    monitoring["total_requests"] += 1

    try:

        response = await call_next(request)

        if 200 <= response.status_code < 400:
            monitoring[
                "successful_requests"
            ] += 1

        elif 400 <= response.status_code < 500:
            monitoring[
                "client_errors"
            ] += 1

        else:
            monitoring[
                "server_errors"
            ] += 1

        return response

    except Exception:

        monitoring[
            "server_errors"
        ] += 1

        raise

    finally:

        duration_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        monitoring[
            "last_response_time_ms"
        ] = duration_ms

        monitoring[
            "total_response_time_ms"
        ] += duration_ms


# fin

@app.get("/health")
def health():

    return {
        "status": "ok",
        "model": MODEL_URI,
    }

# ahouté
@app.get("/metrics")
def metrics():

    total_requests = monitoring[
        "total_requests"
    ]

    if total_requests > 0:

        average_response_time = (
            monitoring[
                "total_response_time_ms"
            ]
            / total_requests
        )

    else:

        average_response_time = 0.0

    return {
        "service": "mini-house-api",
        "model": (
            f"{MODEL_NAME}@{MODEL_ALIAS}"
        ),
        "total_requests": total_requests,
        "successful_requests": monitoring[
            "successful_requests"
        ],
        "client_errors": monitoring[
            "client_errors"
        ],
        "server_errors": monitoring[
            "server_errors"
        ],
        "last_response_time_ms": round(
            monitoring[
                "last_response_time_ms"
            ],
            2,
        ),
        "average_response_time_ms": round(
            average_response_time,
            2,
        ),
    }
# fin

# ajouté
@app.get("/ml-metrics")
def ml_metrics():

    client = MlflowClient()

    model_version = client.get_model_version_by_alias(
        MODEL_NAME,
        MODEL_ALIAS,
    )

    run_id = model_version.run_id

    run = client.get_run(run_id)

    metrics = run.data.metrics

    return {
        "model": MODEL_NAME,
        "alias": MODEL_ALIAS,
        "version": model_version.version,
        "run_id": run_id,
        "train_mae": metrics.get(
            "train_mae"
        ),
        "train_rmse": metrics.get(
            "train_rmse"
        ),
        "train_r2": metrics.get(
            "train_r2"
        ),
        "test_mae": metrics.get(
            "test_mae"
        ),
        "test_rmse": metrics.get(
            "test_rmse"
        ),
        "test_r2": metrics.get(
            "test_r2"
        ),
        "baseline_mae": metrics.get(
            "baseline_mae"
        ),
    }
# fin
# ajouté
@app.get("/drift")
def drift():

    prediction_count = (
        production_monitoring[
            "prediction_count"
        ]
    )

    if prediction_count == 0:

        return {
            "status": (
                "waiting_for_predictions"
            ),
            "prediction_count": 0,
            "threshold_percent": (
                DRIFT_THRESHOLD_PERCENT
            ),
            "overall_drift": False,
            "features": {},
        }


    feature_results = {}

    overall_drift = False


    for feature in [
        "surface",
        "rooms",
        "age",
        "distance_city",
    ]:

        reference_mean = (
            reference_stats[
                "features"
            ][feature]["mean"]
        )

        production_mean = (
            production_monitoring[
                "feature_sums"
            ][feature]
            / prediction_count
        )


        if reference_mean != 0:

            drift_percent = (
                abs(
                    production_mean
                    - reference_mean
                )
                / abs(reference_mean)
            ) * 100

        else:

            drift_percent = 0.0


        drift_detected = (
            drift_percent
            >= DRIFT_THRESHOLD_PERCENT
        )


        if drift_detected:

            overall_drift = True


        feature_results[
            feature
        ] = {
            "reference_mean": round(
                reference_mean,
                2,
            ),
            "production_mean": round(
                production_mean,
                2,
            ),
            "drift_percent": round(
                drift_percent,
                2,
            ),
            "drift_detected": (
                drift_detected
            ),
        }


    return {
        "status": "ok",
        "prediction_count": (
            prediction_count
        ),
        "threshold_percent": (
            DRIFT_THRESHOLD_PERCENT
        ),
        "overall_drift": (
            overall_drift
        ),
        "features": (
            feature_results
        ),
    }
# fin
@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(house: HouseInput):

    input_data = pd.DataFrame(
        [
            {
                "surface": house.surface,
                "rooms": house.rooms,
                "age": house.age,
                "distance_city": (
                    house.distance_city
                ),
            }
        ]
    )
    
    # ajoute
    production_monitoring[
    "prediction_count"
                    ] += 1


    production_monitoring[
    "feature_sums"
                    ]["surface"] += house.surface

    production_monitoring[
    "feature_sums"
            ]["rooms"] += house.rooms

    production_monitoring[
    "feature_sums"
                ]["age"] += house.age

    production_monitoring[
    "feature_sums"
                ]["distance_city"] += (
    house.distance_city
                    )
    # fin

    prediction = model.predict(
        input_data
    )

    predicted_price = float(
        prediction[0]
    )

    return {
        "predicted_price": predicted_price,
        "model": (
            f"{MODEL_NAME}@{MODEL_ALIAS}"
        ),
    }