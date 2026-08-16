select
    surface,
    rooms,
    age,
    distance_city,
    price

from {{ source('raw_data', 'houses') }}

where surface > 0
  and rooms > 0
  and age >= 0
  and distance_city >= 0
  and price > 0