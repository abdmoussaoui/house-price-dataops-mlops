import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    ROOT
    / "warehouse"
    / "house_prices.duckdb"
)

OUTPUT_PATH = (
    ROOT
    / "api"
    / "reference_stats.json"
)


FEATURES = [
    "surface",
    "rooms",
    "age",
    "distance_city",
]


connection = duckdb.connect(
    str(DATABASE_PATH)
)


data = connection.execute("""
    SELECT
        surface,
        rooms,
        age,
        distance_city
    FROM analytics.ml_houses
""").df()


connection.close()


reference_stats = {
    "sample_size": len(data),
    "features": {},
}


for feature in FEATURES:

    reference_stats["features"][
        feature
    ] = {
        "mean": float(
            data[feature].mean()
        ),
        "std": float(
            data[feature].std()
        ),
        "min": float(
            data[feature].min()
        ),
        "max": float(
            data[feature].max()
        ),
    }


with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        reference_stats,
        file,
        indent=4,
    )


print(
    "Statistiques de reference creees :"
)

print(OUTPUT_PATH)

print(
    json.dumps(
        reference_stats,
        indent=4,
    )
)