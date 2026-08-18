import mlflow
import mlflow.sklearn
import pandas as pd


TRACKING_URI = "http://127.0.0.1:5000"

MODEL_NAME = "HousePriceModel"

MODEL_ALIAS = "champion"


mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_registry_uri(TRACKING_URI)


model_uri = (
    f"models:/{MODEL_NAME}"
    f"@{MODEL_ALIAS}"
)


print(
    "Chargement du modèle :",
    model_uri,
)


model = mlflow.sklearn.load_model(
    model_uri
)


new_house = pd.DataFrame(
    [
        {
            "surface": 100.0,
            "rooms": 3,
            "age": 5,
            "distance_city": 4.0,
        }
    ]
)


prediction = model.predict(
    new_house
)


print(
    "\nPrix prédit :",
    prediction[0],
)