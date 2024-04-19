from flask import (Blueprint, render_template, request, flash, redirect, url_for, session)
from sql.connector import get_db_connection, SQL_ROOT_FOLDER
from .utilities import login_required
import os

search_items_view = Blueprint('search_items_view', __name__)


@search_items_view.route('/search-items', methods=['GET'])
@login_required
def search_items():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT * FROM Category ORDER BY category_name;")
            categories = cursor.fetchall()
            # return render_template('search_items.html', categories=categories)
    finally:
        conn.close()
    # session = {'keyword': request.form.get['keyword'], 'category': request.form.get['category']}
    return render_template('search_items.html', categories=categories)


@search_items_view.route('/search-filters', methods=['GET', 'POST'])
@login_required
def search_filters():
    keyword = request.form['keyword']
    category = request.form['category']
    min_price = request.form['min_price']
    if not min_price.isnumeric():
        error_message = 'Minimum price must be a number.'
        render_template('search_items.html', error_message=error_message)
    max_price = request.form['max_price']
    if not max_price.isnumeric():
        error_message = 'Maximum price must be a number.'
        render_template('search_items.html', error_message=error_message)
    condition = request.form['condition']

    session['keyword'] = keyword
    session['category'] = category
    session['min_price'] = min_price
    session['max_price'] = max_price
    session['condition'] = condition

    return redirect(url_for('search_items_view.search_results', keyword=keyword, category=category, min_price=min_price,
                            max_price=max_price, condition=condition, redir_view='search_items_view.search_results'))


@search_items_view.route('/search-results', methods=['GET', 'POST'])
@login_required
def search_results():
    # script_path = f'./sql/search_items.sql'

    keyword = session.get('keyword')
    category = session.get('category')
    min_price = session.get('min_price')
    max_price = session.get('max_price')
    condition = session.get('condition')

    script_path = os.path.join(SQL_ROOT_FOLDER, 'search_items.sql')
    params = tuple()
    with open(script_path, 'r') as file:
        script = file.read()
        # check if inputs exist
        if keyword:
            script += ' AND (Item.item_name LIKE %s or Item.item_description LIKE %s) '
            params += (f'%{keyword}%', f'%{keyword}%')
        if category:
            script += ' AND Item.category_name = %s '
            params += (category,)
        if min_price:
            script += ' AND IFNULL(MaxBidding.bid_amount, Item.starting_bid) >= %s '
            params += (min_price,)
        if max_price:
            script += ' AND IFNULL(MaxBidding.bid_amount, Item.starting_bid) <= %s '
            params += (max_price,)
        if condition:
            script += ' AND CAST(Item.item_condition AS UNSIGNED) <= FIND_IN_SET(%s, "New,Very Good,Good,Fair,Poor") '
            params += (condition,)
        script += ' ORDER BY Item.auction_end_time;'
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(script, params)
            items = cursor.fetchall()
            return render_template('search_results.html', items=items, keyword=keyword, category=category,
                                   min_price=min_price, max_price=max_price, condition=condition)
    finally:
        conn.close()
