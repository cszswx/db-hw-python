SELECT
                  CancelItem.itemID AS `ID`,
                  User.username AS `Listed by`,
                  CancelItem.cancel_date_time AS `Canceled Date`,
                  CancelItem.cancellation_reason AS `Reason`
                FROM
                  CancelItem
                JOIN
                  Item ON CancelItem.itemID = Item.itemID
                JOIN
                  User ON Item.userID = User.userID
                ORDER BY
                  CancelItem.itemID DESC;