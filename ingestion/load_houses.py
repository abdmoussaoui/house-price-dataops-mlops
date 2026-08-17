import csv
from datetime import datetime, timezone
from pathlib import Path

import dlt


CSV_PATH = Path("data/houses.csv")
DATABASE_PATH = "warehouse/house_prices.duckdb"


def read_houses():

    ingestion_time = datetime.now(timezone.utc)

    with CSV_PATH.open("r", encoding="utf-8", newline="") as file:

        reader = csv.DictReader(file)

        for house_id, row in enumerate(reader, start=1):

            yield {
                "house_id": house_id,
                "surface": float(row["surface"]),
                "rooms": int(row["rooms"]),
                "age": int(row["age"]),
                "distance_city": float(row["distance_city"]),
                "price": float(row["price"]),
                "ingested_at": ingestion_time,
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