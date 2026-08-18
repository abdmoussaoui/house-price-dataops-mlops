import mlflow
import mlflow.sklearn
from mlflow import MlflowClient


TRACKING_URI = "http://127.0.0.1:5000"

EXPERIMENT_NAME = "house_price_prediction"

REGISTERED_MODEL_NAME = "HousePriceModel"

MODEL_ARTIFACT_NAME = "model"

CHAMPION_ALIAS = "champion"


mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_registry_uri(TRACKING_URI)


experiment = mlflow.get_experiment_by_name(
    EXPERIMENT_NAME
)


if experiment is None:
    raise RuntimeError(
        f"L'expérience '{EXPERIMENT_NAME}' "
        "n'existe pas."
    )


runs = mlflow.search_runs(
    experiment_ids=[
        experiment.experiment_id
    ],
    filter_string=(
        "attributes.status = 'FINISHED'"
    ),
    order_by=[
        "metrics.test_mae ASC"
    ],
    max_results=1,
)


if runs.empty:
    raise RuntimeError(
        "Aucune run MLflow terminée trouvée."
    )


best_run = runs.iloc[0]


best_run_id = best_run["run_id"]

best_run_name = best_run[
    "tags.mlflow.runName"
]

best_test_mae = best_run[
    "metrics.test_mae"
]

best_test_rmse = best_run[
    "metrics.test_rmse"
]

best_test_r2 = best_run[
    "metrics.test_r2"
]


print("\n--- MEILLEURE RUN ---")

print(
    "Run :",
    best_run_name,
)

print(
    "Run ID :",
    best_run_id,
)

print(
    "MAE :",
    best_test_mae,
)

print(
    "RMSE :",
    best_test_rmse,
)

print(
    "R² :",
    best_test_r2,
)


model_uri = (
    f"runs:/{best_run_id}/"
    f"{MODEL_ARTIFACT_NAME}"
)


print("\nModel URI :")
print(model_uri)


registered_model = mlflow.register_model(
    model_uri=model_uri,
    name=REGISTERED_MODEL_NAME,
)


model_version = registered_model.version


print("\n--- MODEL REGISTRY ---")

print(
    "Nom :",
    REGISTERED_MODEL_NAME,
)

print(
    "Version :",
    model_version,
)


client = MlflowClient()


client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=model_version,
    key="validation_status",
    value="approved",
)


client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=model_version,
    key="problem_type",
    value="regression",
)


client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=model_version,
    key="test_mae",
    value=str(best_test_mae),
)


client.set_registered_model_alias(
    name=REGISTERED_MODEL_NAME,
    alias=CHAMPION_ALIAS,
    version=model_version,
)


client.update_model_version(
    name=REGISTERED_MODEL_NAME,
    version=model_version,
    description=(
        f"Meilleur modèle sélectionné depuis "
        f"l'expérience {EXPERIMENT_NAME}. "
        f"Run: {best_run_name}. "
        f"Test MAE: {best_test_mae:.2f}. "
        f"Test R²: {best_test_r2:.4f}."
    ),
)


print(
    f"\nAlias '{CHAMPION_ALIAS}' "
    f"→ Version {model_version}"
)


champion_uri = (
    f"models:/{REGISTERED_MODEL_NAME}"
    f"@{CHAMPION_ALIAS}"
)


print("\nChampion URI :")

print(champion_uri)