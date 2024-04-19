from flask import (Blueprint, render_template, request, flash, redirect, url_for, session)
from sql.connector import get_db_connection, get_db_connection_multi, SQL_ROOT_FOLDER
from .utilities import get_bid_history, login_required
import pandas as pd
import os

item_description_view = Blueprint('item_description_view', __name__)


@item_description_view.route('/item-description/<int:itemID>', methods=['GET', 'POST'])
@login_required
def item_description(itemID):
    req_form = {}
    if request.method == "GET":
        req_form = request.args
    elif request.method == "POST":
        req_form = request.form
    keyword = req_form.get('keyword')
    category = req_form.get('category')
    min_price = req_form.get('min_price')
    max_price = req_form.get('max_price')
    condition = req_form.get('condition')

    conn = get_db_connection()
    is_admin = session.get('is_admin')
    current_user = session.get('userID')
    script_des = f"""SELECT itemID, item_name , item_description , category_name , item_condition , returnable , get_it_now_price , auction_end_time, userID
                    FROM Item WHERE itemID ={itemID};"""
    # script_min_bid_path = f'./sql/minimum_bid.sql'
    script_min_bid_path = os.path.join(SQL_ROOT_FOLDER, 'minimum_bid.sql')
    try:
        with open(script_min_bid_path, 'r') as file:
            script_min_bid = file.read()
        with conn.cursor() as cursor:
            cursor.execute(script_des)
            item = cursor.fetchall()
            cursor.execute(script_min_bid, (itemID, itemID))
            min_bid = cursor.fetchall()
    finally:
        conn.close()

    # check if current user is the seller
    if item[0]['userID'] == current_user:
        is_seller = True
    else:
        is_seller = False
    df_canceled, df_bid_history = get_bid_history(get_db_connection(), itemID)
    df_bid_history = pd.DataFrame(data=df_bid_history)
    is_auction_end = (item[0]['auction_end_time'] < pd.Timestamp.now()) | (len(df_canceled)>0)



    return render_template('item_description.html', item=item[0], bid_empty=df_bid_history.empty,
                           df_bid_history=df_bid_history, min_bid=min_bid[0]['minimum_bid'],
                           is_admin=is_admin, is_seller=is_seller, is_auction_end=is_auction_end,
                           redir_view='item_description_view.item_description', keyword=keyword, category=category,
                           min_price=min_price, max_price=max_price, condition=condition)


@item_description_view.route('/edit-description', methods=['GET'])
@login_required
def edit_description():
    itemID = request.args.get('itemID')
    new_description = request.args.get('new_description')
    current_user = session.get('userID')
    script = f"""UPDATE Item SET Item.item_description = '{new_description}'
    WHERE Item.itemID = {itemID} AND Item.userID = {current_user};"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            print(script)
            cursor.execute(script)
            conn.commit()
    finally:
        conn.close()
    return redirect(url_for('item_description_view.item_description', itemID=itemID))


@item_description_view.route('/cancel-item', methods=['GET'])
@login_required
def cancel_item():
    itemID = request.args.get('itemID')
    reason = str(request.args.get('reason'))
    is_admin = session.get('is_admin')
    conn = get_db_connection()
    script = f"""INSERT INTO CancelItem (itemID, cancel_date_time, cancellation_reason) VALUES ({itemID}, NOW(), '{reason}');"""

    if is_admin:
        try:
            with conn.cursor() as cursor:
                print(script)
                cursor.execute(script)
                conn.commit()
        finally:
            conn.close()
    return redirect(url_for('search_items_view.search_results'))


@item_description_view.route('/get-it-now', methods=['GET', 'POST'])
@login_required
def get_it_now():
    itemID = request.args.get('itemID')
    get_it_now_price = request.args.get('get_it_now_price')

    conn = get_db_connection_multi()
    script = f"""START TRANSACTION;
    INSERT INTO Bidding (userID, itemID, time_of_bid, bid_amount)
    VALUES ({session.get('userID')}, {itemID}, NOW(), {get_it_now_price});
    UPDATE Item SET Item.auction_end_time =NOW() WHERE Item.itemID = {itemID}; COMMIT;"""
    print(script)
    try:
        with conn.cursor() as cursor:
            cursor.execute(script)
            conn.commit()
    finally:
        conn.close()
    return redirect(url_for('item_description_view.item_description', itemID=itemID))


@item_description_view.route('/bid-on-item', methods=['GET', 'POST'])
@login_required
def bid_on_item():
    itemID = request.args.get('itemID')
    bid_amount = request.args.get('bid')
    conn = get_db_connection()
    script = f"""INSERT INTO Bidding (userID, itemID, time_of_bid, bid_amount) VALUES ({session.get('userID')}, {itemID}, NOW(), {bid_amount});"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(script)
            conn.commit()
    finally:
        conn.close()
    return redirect(url_for('item_description_view.item_description', itemID=itemID))
