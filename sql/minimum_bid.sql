SELECT CASE WHEN ISNULL(MaxBidding.bid_amount) THEN Item.starting_bid+1 ELSE MaxBidding.bid_amount+1 END AS minimum_bid
FROM Item LEFT JOIN (SELECT Bidding.itemID, MAX(Bidding.bid_amount) AS bid_amount
FROM Bidding WHERE Bidding.itemID = %s GROUP BY Bidding.itemID) MaxBidding
ON MaxBidding.itemID = Item.itemID WHERE Item.itemID = %s;