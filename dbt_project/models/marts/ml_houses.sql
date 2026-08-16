select
    surface,
    rooms,
    age,
    distance_city,
    price,

    price / nullif(surface, 0) as price_per_m2

from {{ ref('stg_houses') }}