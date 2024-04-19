#CREATE SCHEMA `team025_p2_schema` ;
USE team025_p2_schema;

CREATE TABLE User (
 userID int unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
 username varchar(50) NOT NULL,
 password varchar(50) NOT NULL,
 first_name varchar(50) NOT NULL,
 last_name varchar(50) NOT NULL,
 CONSTRAINT UNIQUE (username)
);

CREATE TABLE AdminUser (
 userID int unsigned NOT NULL PRIMARY KEY,
 position VARCHAR(50) NOT NULL,
 FOREIGN KEY (userID) REFERENCES User(userID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Category (
 category_name varchar(50) NOT NULL PRIMARY KEY
);

CREATE TABLE Item (
 itemID int NOT NULL PRIMARY KEY,
 item_name varchar(1000) NOT NULL,
 item_description text NOT NULL,
 item_condition enum('New','Very Good','Good','Fair','Poor') NOT NULL,
 returnable boolean NOT NULL,
 starting_bid decimal(10,2) NOT NULL,
 min_sale_price decimal(10,2) NOT NULL,
 get_it_now_price decimal(10,2),
 auction_end_time datetime NOT NULL,
 category_name varchar(50) NOT NULL,
 userID int unsigned NOT NULL,
 FOREIGN KEY (category_name) REFERENCES Category(category_name) ON DELETE CASCADE ON UPDATE CASCADE,
 FOREIGN KEY (userID) REFERENCES User(userID) ON DELETE CASCADE ON UPDATE CASCADE,
 CONSTRAINT PriceCheck CHECK (starting_bid <= min_sale_price AND get_it_now_price >= min_sale_price)
);

CREATE TABLE Bidding (
 userID int unsigned NOT NULL,
 itemID int NOT NULL,
 time_of_bid datetime NOT NULL,
 bid_amount decimal(10,2) NOT NULL,
 FOREIGN KEY (itemID) REFERENCES Item(itemID) ON DELETE CASCADE ON UPDATE CASCADE,
 FOREIGN KEY (userID) REFERENCES `User`(userID) ON DELETE CASCADE ON UPDATE CASCADE,
 CONSTRAINT BidUnique UNIQUE (userID, itemID, time_of_bid)
);

CREATE TABLE Rating (
 itemID int NOT NULL,
 rate_date_time datetime NOT NULL,
 number_of_star int NOT NULL,
 rate_comment text,
 userID int unsigned NOT NULL,
 FOREIGN KEY (itemID) REFERENCES Item(itemID) ON DELETE CASCADE ON UPDATE CASCADE,
 FOREIGN KEY (userID) REFERENCES User(userID) ON DELETE CASCADE ON UPDATE CASCADE,
 CONSTRAINT RatingUnique UNIQUE (itemID, rate_date_time)
);

CREATE TABLE CancelItem (
 itemID int NOT NULL PRIMARY KEY,
 cancel_date_time datetime NOT NULL,
 cancellation_reason text,
 FOREIGN KEY (itemID) REFERENCES Item(itemID) ON DELETE CASCADE ON UPDATE CASCADE
);

ALTER TABLE Rating
ADD CONSTRAINT StarCheck CHECK (number_of_star BETWEEN 0 AND 5);