WITH item_id_match AS (
    SELECT itemID, item_name 
    FROM item 
    WHERE item_name = %s
)
SELECT 
        %s as itemID,
        i.item_name,
        CONCAT(ROUND(AVG(r.number_of_star), 1), ' stars') AS average_rating 
    FROM Rating r 
    INNER JOIN item_id_match i ON r.itemID = i.itemID
    GROUP BY i.item_name;