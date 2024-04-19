SELECT
  (
    SELECT COUNT(*) FROM Item
    WHERE Item.auction_end_time > NOW()
    AND NOT EXISTS (
      SELECT 1 FROM Bidding
      WHERE Bidding.itemID = Item.itemID
      AND (
        (Bidding.bid_amount >= Item.get_it_now_price AND Item.get_it_now_price IS NOT NULL)
        OR (Bidding.bid_amount >= Item.min_sale_price AND Bidding.time_of_bid <= Item.auction_end_time)
      )
    )
    AND NOT EXISTS (SELECT 1 FROM CancelItem WHERE CancelItem.itemID = Item.itemID)
  ) AS 'Auctions Active',

  (
    SELECT COUNT(*) FROM Item
    WHERE NOT EXISTS (SELECT 1 FROM CancelItem WHERE CancelItem.itemID = Item.itemID)
    AND (
      Item.auction_end_time <= NOW()
      OR EXISTS (
        SELECT 1 FROM Bidding
        WHERE Bidding.itemID = Item.itemID
        AND Item.get_it_now_price IS NOT NULL AND Bidding.bid_amount >= Item.get_it_now_price
      )
    )
  ) AS 'Auctions Finished',

  (
    SELECT COUNT(*)
    FROM Item i
    WHERE
    (i.get_it_now_price IS NOT NULL
     AND EXISTS (SELECT 1 FROM Bidding b WHERE b.itemID = i.itemID AND b.bid_amount >= i.get_it_now_price))
    OR (i.auction_end_time <= NOW()
        AND EXISTS (SELECT 1 FROM Bidding b WHERE b.itemID = i.itemID AND b.bid_amount >= i.min_sale_price))
    AND NOT EXISTS (SELECT 1 FROM CancelItem c WHERE c.itemID = i.itemID)
  ) AS 'Auctions Won',

  (SELECT COUNT(*) FROM CancelItem) AS 'Auctions Canceled',

  (SELECT COUNT(DISTINCT Rating.itemID) FROM Rating) AS 'Items Rated',

  (
    SELECT COUNT(*)
    FROM Item i
    WHERE
    ((i.get_it_now_price IS NOT NULL
      AND EXISTS (SELECT 1 FROM Bidding b WHERE b.itemID = i.itemID AND b.bid_amount >= i.get_it_now_price))
    OR (i.auction_end_time <= NOW()
        AND EXISTS (SELECT 1 FROM Bidding b WHERE b.itemID = i.itemID AND b.bid_amount >= i.min_sale_price))
    AND NOT EXISTS (SELECT 1 FROM CancelItem c WHERE c.itemID = i.itemID))
    AND NOT EXISTS (SELECT 1 FROM Rating r WHERE r.itemID = i.itemID)
  ) AS 'Items Not Rated';
