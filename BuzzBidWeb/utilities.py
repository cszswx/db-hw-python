import pandas as pd
import os
from sql.connector import SQL_ROOT_FOLDER
from flask import session, flash, redirect, url_for
from functools import wraps
from sql.connector import get_db_connection

def execute_sql_file(file_name, fetch_all, *args):
    
    res = {}
    sql_file_path = os.path.join(SQL_ROOT_FOLDER, file_name)
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            with open(sql_file_path, 'r') as sql_file:
                sql_command = sql_file.read()
                for s in sql_command.split(';'):
                    if s.strip():
                        cursor.execute(s, args)
                        if fetch_all:
                            res = cursor.fetchall()
                        else:
                            res = cursor.fetchone()
    finally:
        conn.close()
    
    return res

def get_bid_history(db_conn, itemID):
    """
        get bid history, include cancelled items
    """
    canceled_items, bid_history = {}, {}
    query_cancel_item = f"""SELECT CancelItem.cancel_date_time from CancelItem WHERE CancelItem.itemID = {itemID};"""
    sql_file_path = os.path.join(SQL_ROOT_FOLDER, 'bid_history.sql')
    with db_conn.cursor() as cursor:
        cursor.execute(query_cancel_item)
        canceled_items = cursor.fetchall()
        
        with open(sql_file_path, 'r') as sql_file:
            sql_command = sql_file.read()
            for s in sql_command.split(';'):
                if s.strip():
                    cursor.execute(s, (itemID, itemID))
                    bid_history = cursor.fetchall()

    db_conn.close()

    # # df = pd.DataFrame(columns=['Bid Amount', 'Time of Bid', 'Username', 'Status'])
    # df_cancel, df_bid_history = pd.DataFrame(), pd.DataFrame()
    # if len(canceled_items) > 0:
    #     df_cancel = pd.DataFrame(data=canceled_items)
    #     # df_cancel['Status'] = 'Cancelled'
    #     # df = df.append(['Cancelled', canceled_items['cancel_date_time'], 'Administrator', 'Cancelled'])

    # if len(bid_history) > 0:
    #     df_bid_history = pd.DataFrame(data=bid_history)

    return canceled_items, bid_history

def login_required(func):
    @wraps(func)
    def dec_func(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to view this page.', 'warning')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return dec_func


def check_user_logged_in():
    """Check if a user is logged in by verifying if 'username' is in the session.
    Flash a warning message and redirect to the login page if the user is not logged in.

    Returns:
        None if the user is logged in, otherwise a redirect response object.
    """
    if 'username' not in session:
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('auth.login'))
    return None

def has_user_rated(db_conn, userID, itemID):
    res = ()
    with db_conn.cursor() as cursor:
        cursor.execute('SELECT rate_date_time FROM Rating WHERE itemID = %s AND userID = %s', (itemID, userID))
        res = cursor.fetchall()
    db_conn.close()
    
    return len(res) > 0