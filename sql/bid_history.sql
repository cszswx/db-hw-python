WITH BidHistory As (
    SELECT bid_amount,
        time_of_bid,
        username,
        min_sale_price,
        Item.itemID,
        Bidding.userID,
        CASE
            WHEN (
                bid_amount =(
                    SELECT max_bid
                    FROM (
                            SELECT MAX(bid_amount) AS max_bid,
                                itemID
                            FROM Bidding
                            GROUP BY itemID
                        ) AS tmp
                    WHERE tmp.itemID = %s
                )
            )
            AND (bid_amount > Item.min_sale_price) Then Bidding.userID
            ELSE -1
        END AS winner
    FROM Bidding
        LEFT JOIN `User` ON Bidding.userID = User.userID
        LEFT JOIN Item ON Item.itemID = Bidding.itemID
    WHERE Item.itemID = %s
    ORDER BY Bidding.time_of_bid DESC
)
SELECT bid_amount,
    time_of_bid,
    username,
    userID,
    winner
FROM Bidhistory
ORDER BY Bidhistory.time_of_bid DESC