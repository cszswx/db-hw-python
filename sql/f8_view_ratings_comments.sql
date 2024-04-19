WITH item_id_match AS (
    SELECT itemID, item_name 
    FROM item 
    WHERE item_name = %s
),

individual_ratings as (
select 
userID,
r.itemID,
rate_date_time,
number_of_star,
rate_comment
from Rating r
INNER JOIN item_id_match i ON r.itemID = i.itemID
)

select 
u.username,
ir.*
from individual_ratings ir
left join User u
on ir.userID = u.userID
order by rate_date_time desc;
