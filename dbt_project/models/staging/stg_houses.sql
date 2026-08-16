select
    house_id,
    surface,
    rooms,
    age,
    distance_city,
   -- ajouté par akm
    price / nullif(surface, 0) as price_per_m2 ,
    price,
    ingested_at

from {{ source('raw_data', 'houses') }}

where surface > 0
  and rooms > 0
  and age >= 0
  and distance_city >= 0
  and price > 0