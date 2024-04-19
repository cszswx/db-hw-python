from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import pymysql
from .authentication import *
from sql.connector import get_db_connection, SQL_ROOT_FOLDER
import pandas as pd
import os
from .utilities import get_bid_history, login_required, has_user_rated, execute_sql_file
from .forms import SubmitRatingForm, ListItemForm
from datetime import datetime
from datetime import timedelta

views = Blueprint("views", __name__)

# whenever go to this url, it will run function home
@views.route("/")
def home():
    if "username" in session:
        return redirect(url_for("views.main_menu"))

    return render_template("home.html")


# @views.route('/buzzbid/<username>')
@views.route("/main_menu")
@login_required
def main_menu():
    # username = request.args.get('username')
    username = session.get("username", "Guest")  # Default to 'Guest' if not found
    userID = session.get("userID", 0)
    is_admin = session.get("is_admin", False)  # check if the user is admin user
    admin_position = session.get("admin_position", None)
    return render_template(
        "main_menu.html",
        name=username,
        is_admin=is_admin,
        admin_position=admin_position,
        userID=userID,
    )

@views.route("/list-items", methods=["GET", "POST"])
@login_required
def list_items():

    conn = get_db_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT DISTINCT * FROM Category")
        categories = cursor.fetchall()

        category_choices = [(c["category_name"]) for c in categories]

    form = ListItemForm(category_choices)

    if form.validate_on_submit():

        conn = get_db_connection()
        with conn.cursor() as cursor:

            try:
                cursor.execute(
                    "INSERT INTO Item (item_name, item_description, item_condition, returnable, starting_bid, min_sale_price, get_it_now_price, auction_end_time, category_name, userID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        form.name.data,
                        form.description.data,
                        form.condition.data,
                        form.returnable.data,
                        form.starting_bid.data,
                        form.min_sale_price.data,
                        form.get_it_now_price.data,
                        datetime.now()
                        + timedelta(days=float(form.auction_end_time.data)),
                        form.category.data,
                        session.get("userID", 0),
                    ),
                )

                conn.commit()
                return render_template(
                    "error_modal.html",
                    error_message="Item Listed Successfully!",
                    redirect_url="/list-items",
                )

            except:
                print("error")
                error_message = "Please review your listing details"
                return render_template(
                    "error_modal.html",
                    error_message=error_message,
                    redirect_url="/list-items",
                )

    return render_template("list_item.html", form=form)


@views.route("/view-ratings", methods=["GET", "POST"])
@login_required
def view_ratings():

    # check if the user is admin user
    is_admin = session.get("is_admin", False)

    # Viewing ratings logic
    req_form = {}
    if request.method == "GET":
        req_form = request.args
    elif request.method == "POST":
        req_form = request.form

    itemID = req_form.get("itemID", -1)
    item_name = req_form.get("item_name", None)
    winner_ID = req_form.get("winnerID", -1)
    if winner_ID == '': winner_ID = -1
    redir_view = req_form.get('redir_view', 'views.item_results')
    if redir_view == '' : redir_view = 'views.item_results'

    # If a delete action is being requested
    if request.method == "POST":
        action_type = request.form.get("action_type", False)
        if action_type == "delete_rating":
            comment_userID = request.form.get("comment_userID")
            comment_itemID = request.form.get("comment_itemID")
            rate_date_time = request.form.get("rate_date_time")
            itemID = request.form.get("itemID")
            item_name = request.form.get("item_name")

            # Connect to the database and delete the rating
            try:
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM Rating
                        WHERE userID = %s AND itemID = %s AND rate_date_time = %s
                    """,
                        (comment_userID, comment_itemID, rate_date_time),
                    )
                    conn.commit()
                flash("Rating deleted successfully.", "success")
            except Exception as e:
                flash(f"Error deleting rating: {e}", "danger")
            finally:
                if conn:
                    conn.close()

            # Redirect back to the same page to reflect the deletion and prevent form resubmission
            return redirect(
                url_for(
                    "views.view_ratings",
                    itemID=itemID,
                    item_name=item_name,
                    winnerID=winner_ID,
                    redir_view='views.item_results'
                )
            )

    ratings_data = execute_sql_file(
        "f8_view_ratings_summary.sql", False, item_name, itemID
    )
    individual_comments = execute_sql_file(
        "f8_view_ratings_comments.sql", True, item_name
    )

    submit_rate_form = SubmitRatingForm(req_form)
    include_rating = False
    if session["userID"] == int(winner_ID):
        include_rating = not has_user_rated(get_db_connection(), winner_ID, itemID)
        if submit_rate_form.validate_on_submit():
            rating = int(submit_rate_form.rating.data)
            comments = submit_rate_form.comment.data
            conn = get_db_connection()

            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO Rating (itemID, rate_date_time, number_of_star, rate_comment, userID) VALUES (%s, %s, %s, %s, %s)",
                        (itemID, datetime.now(), rating, comments, session["userID"])
                    )
                    conn.commit()
            except:
                return render_template('error_modal.html', error_message = 'Error when submit rating')
            finally:
                if conn: conn.close()

            # refresh current page to display updated ratings
            return redirect(
                url_for(
                    request.endpoint,
                    itemID=itemID,
                    item_name=item_name,
                    winnerID=winner_ID,
                )
            )

    return render_template(
        "view_ratings.html",
        itemID=itemID,
        ratings_data=ratings_data,
        individual_comments=individual_comments,
        is_admin=is_admin,
        include_rating=include_rating,
        submit_rate_form=submit_rate_form,
        redir_view = redir_view
    )

@views.route("/auction-results", methods=['GET', 'POST'])
@login_required
def acution_results():
    result = execute_sql_file("auction_results.sql", True)
    return render_template("auction_results.html", auction_results=result)


@views.route("/item-results", methods=["GET", "POST"])
@login_required
def item_results():
    """
    Siqi
    """
    itemID = request.form["itemID"]
    conn = get_db_connection()
    my_query = f"""SELECT itemID, item_name , item_description , category_name , item_condition , returnable , get_it_now_price , auction_end_time
                FROM Item WHERE itemID ={itemID};"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(my_query)
            result = cursor.fetchall()
    except:
        return render_template('error_modal.html', error_message = f'Error when fetching item: {itemID}')
    finally:
        conn.close()

    df_cancel, df_bid_history = get_bid_history(get_db_connection(), itemID)

    winner_username = False
    has_winner = False
    winnerID = -1

    if (len(df_cancel) == 0) and (len(df_bid_history) > 0):
        has_winner = any(x["winner"] > 0 for x in df_bid_history)
        if has_winner:
            winner_username = df_bid_history[0]["username"]
            winnerID = df_bid_history[0]["userID"]

    return render_template(
        "item_result.html",
        myItem=result[0],
        df_cancel=df_cancel,
        cancelled=len(df_cancel) > 0,
        df_bid_history=df_bid_history,
        has_winner=has_winner,
        winner_username=winner_username,
        winnerID=winnerID,
        redir_view = 'views.item_results'
    )

@views.route("/category-report")
@login_required
def category_report():
    # check if the user is admin user
    is_admin = session.get("is_admin", False)
    if not is_admin:
        flash('Only Admin can view this page. Please login as an admin.')
        return redirect(url_for("views.main_menu"))
    category_data = execute_sql_file('category_report.sql', True)
    if not category_data:
        category_data = []
        flash('No category report data found.', 'info')
    
    return render_template("category_report.html", category_report=category_data)

@views.route("/user-report")
@login_required
def user_report():
    # check if the user is admin user
    is_admin = session.get("is_admin", False)
    if not is_admin:
        flash('Only Admin can view this page. Please login as an admin.')
        return redirect(url_for("views.main_menu"))
    user_report_data = execute_sql_file('user_report.sql', True)
    if not user_report_data:
        user_report_data = []
        flash('No user report data found.', 'info')

    return render_template("user_report.html", user_report=user_report_data)

@views.route("/top-rated-items-report")
@login_required
def top_rated_items_report():
    # check if the user is admin user
    is_admin = session.get("is_admin", False)
    if not is_admin:
        flash('Only Admin can view this page. Please login as an admin.')
        return redirect(url_for("views.main_menu"))
    top_rated_items_data = execute_sql_file('top_rated_items_report.sql', True)
    if not top_rated_items_data:
        top_rated_items_data = []
        flash('No data found for top rated items.', 'info')

    return render_template("top_rated_items.html", top_rated_items=top_rated_items_data)

@views.route("/auction-statistics-report")
@login_required
def auction_statistics_report():
    # check if the user is admin user
    is_admin = session.get("is_admin", False)
    if not is_admin:
        flash('Only Admin can view this page. Please login as an admin.')
        return redirect(url_for("views.main_menu"))
    auction_statistics = execute_sql_file('auction_statistics_report.sql', False)
    if not auction_statistics:
        auction_statistics = {}
        flash('No data found for auction statistics.', 'info')

    return render_template("auction_statistics.html", auction_statistics=auction_statistics)

@views.route("/canceled-auction-details-report")
@login_required
def canceled_auction_details_report():
    # check if the user is admin user
    is_admin = session.get("is_admin", False)
    if not is_admin:
        flash('Only Admin can view this page. Please login as an admin.')
        return redirect(url_for("views.main_menu"))
    canceled_auction_data = execute_sql_file('canceled_auction_details_report.sql', True)
    if not canceled_auction_data:
        flash('No data found for canceled auction.', 'info')

    return render_template("canceled_auction_details.html", canceled_auction=canceled_auction_data)


