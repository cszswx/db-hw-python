import numpy as np
import pandas as pd
import os
import math
import datetime

NOW_TIME = datetime.datetime.now()

def calculate_auction_end_time(df):

    # df_sort = df.sort_values(['bid_timestamp','bid_price'], ascending=False).reset_index(drop = True)
    if not df['bid_timestamp'].any():
        df_tmp = df.squeeze()
    else:
        df_tmp = df.loc[df['bid_price'].idxmax()]
        if df.loc[df['bid_timestamp'].idxmax()]['bid_price'] != df['bid_price'].max():
            raise AssertionError('Latest Bid is not the highest')
    
    df_tmp['end_time'] = np.where(pd.isna(df_tmp['cancellation_timestamp']),
                                  np.where(df_tmp['bid_price'] >= df_tmp['get_it_now_price'], 
                                           df_tmp['bid_timestamp'], df_tmp['scheduled_auction_end']), 
                                  df_tmp['cancellation_timestamp'])
    # df_tmp[''] = np.where(df_tmp['cancellation_timestamp'].isna(), df_tmp['bid_price'], np.nan)
    # df_sort[['sold_price', 'end_time'] ]= df_sort.apply(calculate_sold_px, axis = 1, result_type ='expand')
    # df_sort['sold_price'] = df_sort['sold_price'].max()
    # df_tmp['end_time']
    return df_tmp
 
def calculate_winner_sold_px(row):

    sold_px, winner = None, None

    # if no bidding history
    if pd.isna(row['bid_timestamp']):
        if not pd.isna(row['cancellation_timestamp']):
            winner = 'Cancelled'
        return pd.Series([sold_px, winner])

    # if has bidding history
    if pd.isna(row['cancellation_timestamp']):
        if row['bid_price'] >= row['min_price']:
            winner = row['username_bidding']
            sold_px = row['bid_price']
        else:
            print('d')
    else:
        winner = 'Cancelled'

    return pd.Series([sold_px, winner])
    # sold_px, end_time = None, row['scheduled_auction_end']
    
    # if row['bid_timestamp'] > row['scheduled_auction_end']:
    #     raise AssertionError('Find Bid post after auction scheduled end time!')
    
    # if pd.isna(row['cancellation_timestamp']):
    #     if row['bid_price'] >= row['min_price']:
    #         sold_px = row['bid_price']
    #         if row['bid_price'] >= row['get_it_now_price']:
    #             end_time = row['bid_timestamp']
    # else:
    #     end_time = row['cancellation_timestamp']

    # row['cancellation_timestamp']

    # end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    # return pd.Series([sold_px, end_time])


if __name__ == '__main__':
    df_user = pd.read_csv('Phase_3/demo_data/User.tsv', delimiter='\t')
    df_bid = pd.read_csv('Phase_3/demo_data/Bid.tsv', delimiter='\t')
    df_item = pd.read_csv('Phase_3/demo_data/Items.tsv', delimiter='\t')

    df_reg_user = df_user[df_user['position'].isna()]
    df_admin = df_user[~df_user['position'].isna()]

    ### auction real end time ###
    df_auction = pd.merge(df_item, df_bid, how = 'left', on = 'itemID')
    df_auction = df_auction.groupby('itemID').apply(calculate_auction_end_time).reset_index(drop=True)
    df_auction['end_time'] =  pd.to_datetime(df_auction['end_time'], format='%Y-%m-%d %H:%M:%S')
    df_auction_end = df_auction[df_auction['end_time'] <= NOW_TIME]
    df_auction_live = df_auction[df_auction['end_time'] > NOW_TIME]
    
    # ################## winner & final sold px #############
    df_auction_end[['final _sold_price', 'winner']] = df_auction_end.apply(calculate_winner_sold_px, axis = 1)
    df_auction_end = df_auction_end[['itemID','name','final _sold_price', 'winner', 'end_time']].sort_values('end_time', ascending=False)

    print('done')