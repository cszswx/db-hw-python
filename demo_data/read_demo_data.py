import pymysql
import json
import pandas as pd


file_path = 'sql/DB_CONFIG.json'
with open(file_path, 'r') as file:
    CONFIG = json.load(file)

def get_db_connection():
    connection = pymysql.connect(host=CONFIG['DB_HOST'],
                                user=CONFIG['DB_USER'],
                                password=CONFIG['DB_PASSWORD'],
                                database=CONFIG['DB_DB'],
                                charset="utf8mb4",
                                cursorclass=pymysql.cursors.DictCursor)
    return connection

# create table
print('create table')
sql_file_path = 'demo_data/creat_table.sql'
conn = get_db_connection()
with conn.cursor() as cursor:
    with open(sql_file_path, 'r') as sql_file:
        sql_command = sql_file.read()
        for s in sql_command.split(';'):
            if s.strip():
                cursor.execute(s)
        conn.commit()
#conn.close()

# insert User
print('inserting user')
user = pd.read_csv("demo_data/User.tsv", delimiter='\t')
user.index = range(1, len(user) + 1)
#conn = get_db_connection()
with conn.cursor() as cursor:
     for i in range(1,user.shape[0]+1):
         username = user['username'][i]
         password = user['password'][i]
         first_name = user['first_name'][i]
         last_name = user['last_name'][i]
         cursor.execute("""INSERT INTO `User` (username, password, first_name, last_name)
         VALUES (%s, %s,%s,%s)""",(username, password, first_name, last_name))
     conn.commit()
#conn.close()


# insert Admin User
print('inserting Admin User')
admin_user = user['position'].dropna()
#conn = get_db_connection()
with conn.cursor() as cursor:
     for i, v in admin_user.items():
         userID = i
         position = v
         cursor.execute("""INSERT INTO AdminUser (userID,position) VALUES (%s,%s)""",(userID,position))
     conn.commit()
#conn.close()



# insert category
print('inserting Category')
item = pd.read_csv("demo_data/Items.tsv", delimiter='\t')
conn = get_db_connection()
with conn.cursor() as cursor:
     for c in item['category_name'].unique():
         cursor.execute("""INSERT INTO Category (category_name) VALUES (%s)""",(c, ))
     conn.commit()
#conn.close()



# insert item
print('inserting Item')
user.reset_index(inplace=True)
user.rename(columns={'index': 'userID'}, inplace=True)
item_merged = pd.merge(item, user, left_on = 'username_listed', right_on= 'username', how = 'left')
item_merged = item_merged[['userID'] + [col for col in item.columns]]
item_merged = item_merged.apply(lambda x: x.map(lambda y: None if pd.isna(y) else y))
item_merged['get_it_now_price'] = item_merged['get_it_now_price'].astype(object)
item_merged['num_stars'] = item_merged['num_stars'].astype(object)
item_merged['get_it_now_price'] = item_merged['get_it_now_price'].where(item_merged['get_it_now_price'].notna(), other=None)
item_merged['num_stars'] = item_merged['num_stars'].where(item_merged['num_stars'].notna(), other=None)
                  
#conn = get_db_connection()
with conn.cursor() as cursor:
     for i in range(item_merged.shape[0]):
         itemID = item_merged['itemID'][i]
         item_name = item_merged['name'][i]
         item_description = item_merged['description'][i]
         item_condition = item_merged['condition'][i]
         returnable = item_merged['returns_accepted'][i]
         starting_bid = item_merged['start_price'][i]
         min_sale_price = item_merged['min_price'][i]
         get_it_now_price = item_merged['get_it_now_price'][i]
         auction_end_time = item_merged['scheduled_auction_end'][i]
         category_name = item_merged['category_name'][i]
         userID = item_merged['userID'][i]
         cursor.execute("""INSERT INTO Item (itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, get_it_now_price, auction_end_time, category_name, userID)
         VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",(itemID, item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, get_it_now_price, auction_end_time, category_name, userID))
     conn.commit()
#conn.close()

# insert CancelItem
print('inserting CancelItem')
cancel_item = item_merged[['itemID','cancellation_timestamp','cancellation_reason']].dropna(subset=['cancellation_timestamp'])
#conn = get_db_connection()
with conn.cursor() as cursor:
     for i in cancel_item.index:
         itemID = cancel_item['itemID'][i]
         cancel_date_time = cancel_item['cancellation_timestamp'][i]
         cancellation_reason = cancel_item['cancellation_reason'][i]
         cursor.execute("""INSERT INTO CancelItem (itemID, cancel_date_time, cancellation_reason)
         VALUES (%s, %s, %s)""",(itemID, cancel_date_time, cancellation_reason))
     conn.commit()
#conn.close()

# insert Bidding
print('inserting Bidding')
bid = pd.read_csv("demo_data/Bid.tsv", delimiter='\t')
bid_merged = pd.merge(bid, user, left_on = 'username_bidding', right_on= 'username', how = 'left')
bid_merged = bid_merged[['userID'] + [col for col in bid.columns]]
#conn = get_db_connection()
with conn.cursor() as cursor:
     for i in range(bid_merged.shape[0]):
         userID = bid_merged['userID'][i]
         itemID = bid_merged['itemID'][i]
         time_of_bid = bid_merged['bid_timestamp'][i]
         bid_amount = bid_merged['bid_price'][i]
         cursor.execute("""INSERT INTO Bidding (userID, itemID, time_of_bid, bid_amount)
         VALUES (%s, %s, %s, %s)""",(userID, itemID, time_of_bid, bid_amount))
     conn.commit()
#conn.close()

# insert Rating
print('inserting Rating')
bid_merged_winner = bid_merged.sort_values(by=['itemID', 'bid_timestamp', 'bid_price'], ascending=[True, False, False])
bid_merged_winner = bid_merged_winner.groupby('itemID').first().reset_index()
rating = item_merged[['itemID','rate_timestamp','num_stars','rating_comment']].dropna()
rating_w_winner = pd.merge(rating, bid_merged_winner, left_on = 'itemID', right_on= 'itemID', how = 'left')
rating_w_winner = rating_w_winner[['userID'] + [col for col in rating.columns]]
#conn = get_db_connection()
with conn.cursor() as cursor:
     for i in range(rating_w_winner.shape[0]):
         itemID = rating_w_winner['itemID'][i]
         rate_date_time = rating_w_winner['rate_timestamp'][i]
         number_of_star = rating_w_winner['num_stars'][i]
         rate_comment = rating_w_winner['rating_comment'][i]
         userID = rating_w_winner['userID'][i]
         cursor.execute("""INSERT INTO Rating (itemID, rate_date_time, number_of_star, rate_comment, userID)
         VALUES (%s, %s, %s, %s, %s)""",(itemID, rate_date_time, number_of_star, rate_comment, userID))
     conn.commit()
conn.close()

print("COMPLETED")

