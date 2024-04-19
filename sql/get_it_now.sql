INSERT INTO Bidding (userID, itemID, time_of_bid, bid_amount);
SELECT '$CurrentUser', Item.itemID ,NOW(), Item.get_it_now_price
FROM Item WHERE Item.itemID = '$ItemID' AND EXISTS (SELECT Item.get_it_now_price FROM Item where Item.itemID = '$ItemID');
UPDATE Item SET Item.auction_end_time =NOW() WHERE Item.itemID = '$ItemID';