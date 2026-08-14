import csv
from pathlib import Path

import dlt


CSV_PATH = Path("data/houses.csv")
DATABASE_PATH = "warehouse/house_prices.duckdb"


def read_houses():
    with CSV_PATH.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            yield {
                "surface": float(row["surface"]),
                "rooms": int(row["rooms"]),
                "age": int(row["age"]),
                "distance_city": float(row["distance_city"]),
                "price": float(row["price"]),
            }


pipeline = dlt.pipeline(
    pipeline_name="house_ingestion",
    destination=dlt.destinations.duckdb(DATABASE_PATH),
    dataset_name="raw_data",
)


load_info = pipeline.run(
    read_houses(),
    table_name="houses",
    write_disposition="replace",
)


print(load_info)