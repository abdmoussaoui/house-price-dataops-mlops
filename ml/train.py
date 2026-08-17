from pathlib import Path

import duckdb
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split


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

print("\nMAE :", mae)
print("RMSE :", rmse)
print("R² :", r2)