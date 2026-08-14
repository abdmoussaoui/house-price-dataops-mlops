import csv
from pathlib import Path


data_path = Path("data/houses.csv")

with data_path.open("r", encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)
    rows = list(reader)


print("Colonnes :", reader.fieldnames)
print("Nombre de logements :", len(rows))

print("\nPremiers logements :")

for row in rows[:3]:
    print(row)