select
    house_id,
    surface,
    rooms,
    age,
    distance_city,
    price ,
    -- ajouté par akm
    price / nullif(surface, 0) as price_per_m2 ,
    -- ingested_at

from {{ ref('stg_houses') }}

where surface > 0
  and rooms > 0
  and age >= 0
  and distance_city >= 0
  and price > 0