SELECT
                  Item.item_name AS `Item Name`,
                  ROUND(AVG(Rating.number_of_star), 1) AS `Average Rating`,
                  COUNT(Rating.itemID) AS `Rating Count`
                FROM
                  Item
                INNER JOIN Rating ON Item.itemID = Rating.itemID
                WHERE
                  Rating.number_of_star IS NOT NULL
                GROUP BY
                  Item.item_name
                ORDER BY
                  `Average Rating` DESC,
                  `Item Name` ASC
                LIMIT 10;