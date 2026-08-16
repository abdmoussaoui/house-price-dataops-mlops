select *

from {{ source('raw_data', 'houses') }}

where surface <= 0
   or rooms <= 0
   or age < 0
   or distance_city < 0
   or price <= 0