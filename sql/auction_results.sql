-- get max bidding for each item
WITH MaxBidding AS (
	SELECT TmpBidding.itemID,
		TmpBidding.bid_amount,
		Bidding.userID,
		Bidding.time_of_bid,
		User.username
	FROM (
			SELECT Bidding.itemID,
				MAX(Bidding.bid_amount) as bid_amount
			FROM Bidding
			GROUP BY Bidding.itemID
		) AS TmpBidding
		LEFT JOIN Bidding ON TmpBidding.itemID = Bidding.itemID
		AND TmpBidding.bid_amount = Bidding.bid_amount
		LEFT JOIN `User` ON User.userID = Bidding.userID
),
AuctionEndedItems AS (
	SELECT itemID,
		item_name,
		real_auction_end_time,
		cancel_date_time,
		min_sale_price,
		bid_amount,
		userID,
		username
	FROM (
			SELECT Item.itemID,
				item_name,
				auction_end_time,
				cancel_date_time,
				min_sale_price,
				get_it_now_price,
				bid_amount,
				time_of_bid,
				username,
				MaxBidding.userID,
				CASE
					WHEN bid_amount > get_it_now_price THEN time_of_bid
					ELSE auction_end_time
				END AS real_auction_end_time
			FROM Item
				LEFT JOIN CancelItem ON Item.itemID = CancelItem.itemID
				LEFT JOIN MaxBidding ON Item.itemID = MaxBidding.itemID
		) As tmpTab
	WHERE LEAST(
			real_auction_end_time,
			IFNULL(cancel_date_time, '3000-01-01')
		) < NOW()
),
-- for each item, find its max bidding and user who bids the highest
AuctionRes AS (
	SELECT AuctionEndedItems.itemID,
		item_name,
		real_auction_end_time,
		cancel_date_time,
		bid_amount,
		min_sale_price,
		userID,
		CASE
			WHEN ISNULL(cancel_date_time) THEN CASE
				WHEN (bid_amount >= min_sale_price) THEN username
				ELSE ""
			END
			ELSE "Cancelled"
		END AS winner,
		CASE
			WHEN ISNULL(cancel_date_time) THEN CASE
				WHEN (bid_amount >= min_sale_price) THEN bid_amount
				ELSE ""
			END
			ELSE ""
		END AS winner_bid_amount
	FROM AuctionEndedItems
)
SELECT itemID,
	item_name,
	winner_bid_amount,
	winner,
	CASE
		WHEN ISNULL(AuctionRes.cancel_date_time) THEN AuctionRes.real_auction_end_time
		ELSE AuctionRes.cancel_date_time
	END As end_time
FROM AuctionRes
ORDER BY end_time DESC;