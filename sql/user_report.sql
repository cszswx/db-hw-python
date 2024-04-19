SELECT
  u.username as Username,
  (SELECT COUNT(*) FROM Item i WHERE i.userID = u.userID) AS Listed,
  (SELECT COUNT(DISTINCT i.itemID)
   FROM Item i
   JOIN Bidding b ON i.itemID = b.itemID
   WHERE i.userID = u.userID AND
     ( (b.bid_amount >= i.get_it_now_price AND i.get_it_now_price IS NOT NULL) OR
       (i.auction_end_time <= NOW() AND b.bid_amount >= i.min_sale_price) ) AND
     NOT EXISTS (SELECT 1 FROM CancelItem c WHERE c.itemID = i.itemID)
  ) AS Sold,
  (SELECT COUNT(*)
   FROM Bidding b
   WHERE b.userID = u.userID AND
     b.bid_amount >= ALL (SELECT b2.bid_amount FROM Bidding b2 WHERE b2.itemID = b.itemID AND b2.time_of_bid <= NOW()) AND
     b.bid_amount >= (SELECT i.min_sale_price FROM Item i WHERE i.itemID = b.itemID) AND
     NOT EXISTS (SELECT 1 FROM CancelItem c WHERE c.itemID = b.itemID) AND
     EXISTS (SELECT 1 FROM Item i WHERE i.itemID = b.itemID AND i.auction_end_time <= NOW())
  ) AS Won,
  (SELECT COUNT(*) FROM Rating r WHERE r.userID = u.userID) AS Rated,
  COALESCE((
    SELECT i.item_condition
    FROM Item i
    WHERE i.userID = u.userID
    GROUP BY i.item_condition
    ORDER BY COUNT(*) DESC,
             FIELD(i.item_condition, 'Poor', 'Fair', 'Good', 'Very Good', 'New') ASC
    LIMIT 1
  ), 'N/A') AS 'Most Frequent Condition'
FROM User u
ORDER BY Listed DESC, u.username;