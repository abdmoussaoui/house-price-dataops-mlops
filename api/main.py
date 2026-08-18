from contextlib import asynccontextmanager

import mlflow
import mlflow.sklearn
import pandas as pd

from fastapi import FastAPI
from pydantic import BaseModel, Field


TRACKING_URI = "http://127.0.0.1:5000"

MODEL_NAME = "HousePriceModel"

MODEL_ALIAS = "champion"

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


@app.get("/health")
def health():

    return {
        "status": "ok",
        "model": MODEL_URI,
    }


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