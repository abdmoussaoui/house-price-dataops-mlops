import duckdb


DATABASE_PATH = "warehouse/house_prices.duckdb"


connection = duckdb.connect(DATABASE_PATH)


print("\n--- TABLES ---")

tables = connection.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables
    ORDER BY table_schema, table_name
""").fetchall()

for table in tables:
    print(table)


print("\n--- STRUCTURE DE raw_data.houses ---")

columns = connection.execute("""
    DESCRIBE raw_data.houses
""").fetchall()

for column in columns:
    print(column)


print("\n--- 5 PREMIERS LOGEMENTS ---")

houses = connection.execute("""
    SELECT *
    FROM raw_data.houses
    LIMIT 5
""").fetchall()

for house in houses:
    print(house)


print("\n--- NOMBRE DE LOGEMENTS ---")

count = connection.execute("""
    SELECT COUNT(*)
    FROM raw_data.houses
""").fetchone()[0]

print(count)


print("\n--- STATISTIQUES PRIX ---")

statistics = connection.execute("""
    SELECT
        AVG(price) AS average_price,
        MIN(price) AS minimum_price,
        MAX(price) AS maximum_price
    FROM raw_data.houses
""").fetchone()

print("Prix moyen :", statistics[0])
print("Prix minimum :", statistics[1])
print("Prix maximum :", statistics[2])


# ajouté  : apres la creation de marts pour machine learning :


print("\n--- STRUCTURE DE analytics.stg_houses ---")

columnss = connection.execute("""
    DESCRIBE analytics.stg_houses
""").fetchall()

for column in columnss:
    print(column)
    
    
    

print("\n--- STRUCTURE DE analytics.ml_houses ---")

columnss = connection.execute("""
    DESCRIBE analytics.ml_houses
""").fetchall()

for column in columnss:
    print(column)

mart = connection.execute("""
    SELECT *
FROM analytics.ml_houses
LIMIT 5
""").fetchall()

print("Mart :")

for el in mart:
    print(el)
    
    
# verification apres staging et marts

import duckdb


connection = duckdb.connect("warehouse/house_prices.duckdb")


print("\n--- RAW ---")

print(
    connection.execute("""
        SELECT COUNT(*)
        FROM raw_data.houses
    """).fetchone()
)


print("\n--- STAGING ---")

print(
    connection.execute("""
        SELECT COUNT(*)
        FROM analytics.stg_houses
    """).fetchone()
)


print("\n--- ML DATA ---")

rows = connection.execute("""
    SELECT *
    FROM analytics.ml_houses
    LIMIT 5
""").fetchall()

for row in rows:
    print(row)


connection.close()

