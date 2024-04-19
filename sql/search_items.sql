SELECT Item.itemID  ,Item.item_name
	,CASE WHEN ISNULL(CancelItem.cancel_date_time) THEN MaxBidding.bid_amount ELSE NULL END AS bid_amount
	,CASE WHEN ISNULL(CancelItem.cancel_date_time) THEN User.username ELSE NULL END AS username
	, Item.get_it_now_price, Item.auction_end_time
FROM Item LEFT JOIN (SELECT Bidding.itemID , MAX(Bidding.bid_amount) as bid_amount FROM Bidding GROUP BY Bidding.itemID) MaxBidding ON Item.itemID =MaxBidding.itemID
		LEFT JOIN Bidding  ON MaxBidding.itemID = Bidding.itemID AND MaxBidding.bid_amount = Bidding.bid_amount
		LEFT JOIN User ON Bidding.userID = User.userID
		LEFT JOIN CancelItem ON Item.itemID = CancelItem.itemID
WHERE
Item.itemID NOT IN (SELECT CancelItem.itemID FROM CancelItem)
AND Item.auction_end_time >= Now()