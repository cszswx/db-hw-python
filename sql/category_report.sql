SELECT
      Item.category_name AS `Category`,
      COUNT(Item.itemID) AS `Total Items`,
      ROUND(MIN(Item.get_it_now_price), 2) AS `Min Price`,
      ROUND(MAX(Item.get_it_now_price), 2) AS `Max Price`,
      ROUND(AVG(Item.get_it_now_price), 2) AS `Average Price`
    FROM
      Item
    WHERE Item.itemID not in
    (SELECT distinct itemID FROM CancelItem)
    GROUP BY
      Item.category_name
    ORDER BY
      `Category` ASC;