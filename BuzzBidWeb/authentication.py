"""
    Authentication to buzzbid account:
        1) log in
        2) log out
        3) sign up
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from sql.connector import get_db_connection
from .forms import *
from .views import *
import pymysql
from .utilities import *

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("views.main_menu"))
    
    form = LogInForm()
    # validate form
    if form.validate_on_submit():
        print("submit")
        # Check if the login button was used
        if "login" in request.form:
            username = form.username.data
            password = form.password.data
            conn = get_db_connection()
            user = None
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM User WHERE username = %s AND password = %s",
                        (username, password),
                    )
                    user = cursor.fetchone()

                    if user:
                        # process login
                        print(user.keys())
                        # Check if user is an admin
                        cursor.execute(
                            "SELECT position FROM adminuser WHERE userID = %s",
                            (user["userID"],),
                        )
                        admin = cursor.fetchone()

                        if admin:
                            session["is_admin"] = True
                            session["admin_position"] = admin["position"]
                        else:
                            session["is_admin"] = False
                        session["username"] = username
                        userID = user["userID"]
                        session["userID"] = userID
            finally:
                conn.close()
                if user:
                    print("error")
                    error_message = (
                        "Logged in Successfully! Redirecting to Main Menu."
                    )
                    return render_template(
                        "error_modal.html",
                        error_message=error_message,
                        redirect_url=url_for('views.main_menu', _external=True) + f"?username={username}&userID={userID}",
                    )
                    
                    #flash("Logged in Successfully!", "success")
                    #return redirect(
                    #    url_for("views.main_menu", username=username, userID=userID)
                    #)
                else:
                    flash("Invalid username or password. Please try again.", "danger")
        # Check if the register button was clicked
        elif "register" in request.form:
            print("register")
            return redirect(
                url_for("auth.sign_up")
            )  # Redirect to the registration view
    return render_template("login.html", title="Login", form=form)


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if "username" in session:
        return redirect(url_for("views.main_menu"))
    
    form = SignUpForm()
    if form.validate_on_submit():
        # Check if passwords match
        if form.psw1.data != form.psw2.data:
            flash("Password does not match. Please try again.", "warning")
            return render_template("sign_up.html", form=form)

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if the username already exists
                cursor.execute(
                    "SELECT * FROM User WHERE username = %s", (form.username.data,)
                )
                if cursor.fetchone():
                    # Username already exists
                    flash(
                        "This username is already signed up. Please choose another username or login.",
                        "warning",
                    )
                else:
                    # Username does not exist, proceed with account creation
                    cursor.execute(
                        "INSERT INTO User (username, password, first_name, last_name) VALUES (%s, %s, %s, %s)",
                        (
                            form.username.data,
                            form.psw1.data,
                            form.first_name.data,
                            form.last_name.data,
                        ),
                    )
                    conn.commit()
                    print("error")
                    error_message = (
                        "Account created successfully! Redirecting to Login."
                    )
                    return render_template(
                        "error_modal.html",
                        error_message=error_message,
                        redirect_url="/login",
                    )
                    #flash("Account created successfully!", "success")
                    #return redirect(url_for("auth.login"))
        except pymysql.MySQLError as e:
            # Rollback the transaction in case of any exception
            conn.rollback()
            flash("Failed to create account. Please try again.", "danger")
        finally:
            conn.close()
    return render_template("sign_up.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    # Clear all data from the session
    # login_check = check_user_logged_in()
    # if login_check is not None:
    #     return login_check

    session.clear()
    print("error")
    error_message = (
        "You have been logged out successfully."
    )
    return render_template(
        "error_modal.html",
        error_message=error_message,
        redirect_url="/login",
    )
    
    #return redirect(url_for("views.home"))
