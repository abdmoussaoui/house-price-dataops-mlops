import mlflow
import mlflow.sklearn

from pathlib import Path

import duckdb
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split

# ------------------------------------
mlflow.set_tracking_uri(
    "http://127.0.0.1:5000"
)

mlflow.set_experiment(
    "house_price_prediction"
)

# -------------------------------------

ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = ROOT / "warehouse" / "house_prices.duckdb"


connection = duckdb.connect(str(DATABASE_PATH))


data = connection.execute("""
    SELECT
        surface,
        rooms,
        age,
        distance_city,
        price
    FROM analytics.ml_houses
""").df()


connection.close()


print("\n--- DATASET ---")
print(data)


X = data[
    [
        "surface",
        "rooms",
        "age",
        "distance_city",
    ]
]

y = data["price"]


print("\n--- FEATURES X ---")
print(X.head())


print("\n--- TARGET y ---")
print(y.head())


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
)


print("\n--- SPLIT ---")
print("Train :", len(X_train))
print("Test  :", len(X_test))


model = LinearRegression()


model.fit(
    X_train,
    y_train,
)

train_predictions = model.predict(X_train)

train_mae = mean_absolute_error(
    y_train,
    train_predictions,
)

train_rmse = root_mean_squared_error(
    y_train,
    train_predictions,
)

train_r2 = r2_score(
    y_train,
    train_predictions,
)


predictions = model.predict(X_test)


mae = mean_absolute_error(
    y_test,
    predictions,
)

rmse = root_mean_squared_error(
    y_test,
    predictions,
)

r2 = r2_score(
    y_test,
    predictions,
)


print("\n--- RESULTATS ---")

print("Valeurs réelles :")
print(y_test.to_numpy())

print("\nPrédictions :")
print(predictions)

print("\n--- LINEAR REGRESSION ---")


print("\nMAE :", mae)
print("RMSE :", rmse)
print("R² :", r2)


baseline_predictions = [
    y_train.mean()
] * len(y_test)

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions,
)

print("MAE baseline :", baseline_mae)


print("\n--- LINEAR REGRESSION : TRAIN ---")
print("MAE :", train_mae)
print("RMSE :", train_rmse)
print("R² :", train_r2)

print("\n--- LINEAR REGRESSION : TEST ---")
print("MAE :", mae)
print("RMSE :", rmse)
print("R² :", r2)


# added for mlflow

with mlflow.start_run(
    run_name="linear_regression"
):

    mlflow.log_param(
        "model_type",
        "LinearRegression",
    )

    mlflow.log_param(
        "test_size",
        0.20,
    )

    mlflow.log_param(
        "random_state",
        42,
    )

    mlflow.log_metric(
        "train_mae",
        train_mae,
    )

    mlflow.log_metric(
        "train_rmse",
        train_rmse,
    )

    mlflow.log_metric(
        "train_r2",
        train_r2,
    )

    mlflow.log_metric(
        "test_mae",
        mae,
    )

    mlflow.log_metric(
        "test_rmse",
        rmse,
    )

    mlflow.log_metric(
        "test_r2",
        r2,
    )

    mlflow.log_metric(
        "baseline_mae",
        baseline_mae,
    )

    mlflow.sklearn.log_model(
        sk_model=model,
        name="model",
        input_example=X_train.head(3),
    )

# random forest

random_forest = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
)

random_forest.fit(
    X_train,
    y_train,
)

rf_train_predictions = random_forest.predict(
    X_train
)

rf_train_mae = mean_absolute_error(
    y_train,
    rf_train_predictions,
)

rf_train_rmse = root_mean_squared_error(
    y_train,
    rf_train_predictions,
)

rf_train_r2 = r2_score(
    y_train,
    rf_train_predictions,
)


rf_predictions = random_forest.predict(X_test)

rf_mae = mean_absolute_error(
    y_test,
    rf_predictions,
)

rf_rmse = root_mean_squared_error(
    y_test,
    rf_predictions,
)

rf_r2 = r2_score(
    y_test,
    rf_predictions,
)


print("\n--- RANDOM FOREST ---")

print("MAE :", rf_mae)
print("RMSE :", rf_rmse)
print("R² :", rf_r2)

print("\n--- RANDOM FOREST : TRAIN ---")
print("MAE :", rf_train_mae)
print("RMSE :", rf_train_rmse)
print("R² :", rf_train_r2)

print("\n--- RANDOM FOREST : TEST ---")
print("MAE :", rf_mae)
print("RMSE :", rf_rmse)
print("R² :", rf_r2)



#  added for mlflow

with mlflow.start_run(
    run_name="random_forest"
):

    mlflow.log_param(
        "model_type",
        "RandomForestRegressor",
    )

    mlflow.log_param(
        "n_estimators",
        100,
    )

    mlflow.log_param(
        "random_state",
        42,
    )

    mlflow.log_param(
        "test_size",
        0.20,
    )

    mlflow.log_metric(
        "train_mae",
        rf_train_mae,
    )

    mlflow.log_metric(
        "train_rmse",
        rf_train_rmse,
    )

    mlflow.log_metric(
        "train_r2",
        rf_train_r2,
    )

    mlflow.log_metric(
        "test_mae",
        rf_mae,
    )

    mlflow.log_metric(
        "test_rmse",
        rf_rmse,
    )

    mlflow.log_metric(
        "test_r2",
        rf_r2,
    )

    mlflow.log_metric(
        "baseline_mae",
        baseline_mae,
    )

    mlflow.sklearn.log_model(
        sk_model=random_forest,
        name="model",
        input_example=X_train.head(3),
    )
