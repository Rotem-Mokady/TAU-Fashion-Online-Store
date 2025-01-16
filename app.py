from flask import Flask, redirect, render_template, request, url_for, session
import os
from typing import Dict

from register_utils import (
    validate_email_template, validate_username_template, validate_password_template,
    ensure_new_user, register_new_user, ensure_minimum_age
)
from auth_utils import signing_in_response, is_admin
from cloths_data_handler import (
    ClothsDataCollection
)
from admins_updating_handler import UpdateClothsTable
from order_summary_utils import get_product_full_details, generate_summary_info, add_transaction_to_db, \
    update_products_inventory

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def sign_in():
    # if there is an open session the user - go directly to home page
    if session.get('username'):
        return redirect(url_for("home_page"))

    # go to sign in HTML template
    return render_template("sign_in.html")


@app.route('/sign_in', methods=['POST'])
def sign_in_auth_handler():
    # get username and password from client's request, and return a boolean response for the authentication trying.
    username, password = request.form['username'], request.form['password']
    resp = signing_in_response(username=username, password=password)

    # if the user is already known, save his name in the session and send him to home page
    if resp:
        session['username'] = username
        return redirect(url_for("home_page"))

    # go back to sign in page if the user is not familiar, and present a relevant error message
    error_message = "Invalid username or password. Please try again."
    return render_template("sign_in.html", error_message=error_message)


@app.route('/sign_up')
def sign_up():
    # go to sign up HTML template
    return render_template("sign_up.html")


@app.route('/sign_up_handler', methods=['POST'])
def sign_up_registration_handler():
    # get all parameters from client's request
    email, username = request.form['email'], request.form['username']
    password, confirmed_password = request.form['password'], request.form['confirm_password']
    birth_date_str = request.form['birth_date']

    # make some validation checks on user's private details
    email_resp = validate_email_template(email)
    username_resp = validate_username_template(username)
    password_resp = validate_password_template(password)

    # make sure that the user is not already signed in, and it's age is over the minimum
    is_new = ensure_new_user(email=email, username=username)
    is_eighteen = ensure_minimum_age(birth_date_str=birth_date_str)

    # go back to sign up page and send an appropriate error message if needed

    if not (email_resp and username_resp and password_resp):
        error_message = "Invalid email address, username or password. Please try again."
        return render_template("sign_up.html", error_message=error_message)

    elif password != confirmed_password:
        error_message = "Two different passwords entered. Please try again."
        return render_template("sign_up.html", error_message=error_message)

    elif not is_new:
        error_message = "Email or username is already in use."
        return render_template("sign_up.html", error_message=error_message)

    elif not is_eighteen:
        error_message = "Your age is under the age limitation."
        return render_template("sign_up.html", error_message=error_message)

    # after the new user passed all validations tests:
    # register, save his name and send him to home page

    register_new_user(request_data=request.form)
    session['username'] = username
    return redirect(url_for("home_page"))


@app.route('/home_page')
def home_page():
    # go back to sign in page if the username is not familiar in the session
    username = session.get('username')
    if not username:
        return render_template("sign_in.html")

    # collect the data of the products from the DB or from the session if exists
    if not session.get('home_page_table'):
        cloths = ClothsDataCollection()
        table = cloths.home_page_data_to_html
        session['home_page_table'] = table
    else:
        table = session['home_page_table']

    # collect the current success message and the current summary details from the order process
    order_summary_success_message = request.args.get('success_message', default=None)
    order_summary_info = session.get('order_summary_info', default=None)

    # If the user approved his order and he has an actual reservation
    if order_summary_success_message and order_summary_info:
        # set a new order with no products on the following order
        session['order_summary_info'] = None
        # create a new transaction and insert it to the DB
        add_transaction_to_db(username=username, data=order_summary_info)
        # subtract the ordered amount of each product from it's total inventory, and update in the DB
        update_products_inventory(transaction_data=order_summary_info)

        # now we need to show a different data about the inventory
        # collect the data from the DB again and store in the session
        cloths = ClothsDataCollection()
        table = cloths.home_page_data_to_html
        session['home_page_table'] = table

    # if the user is not an admin and he tried to move to administrations' page, show him why he can't do that
    not_admin_message_error = request.args.get('error_message', default=None)
    # go the home page HTML template, send all relevant variables
    return render_template(
        "home_page.html", username=username, table=table,
        success_message=order_summary_success_message, error_message=not_admin_message_error
    )


@app.route('/order_summary', methods=['GET', 'POST'])
def order_summary():
    # get the username and his order from the session
    username, home_page_table = session.get('username'), session.get('home_page_table')
    # go back to home page if from some reason one of the parameters is missing
    if not username or not home_page_table:
        return redirect(url_for('home_page'))

    # set an empty order table
    table = []
    # iterate all products details from user's order
    for key in request.form:
        # focus only on "Your Order" parameter (the HTML tag is defined as "product_{product_id}")
        if key.startswith('product_'):

            # extract the product id and the amount of it in the current order
            product_id = int(key.split('_')[1])
            amount = float(request.form[key])

            # buy only if the user actually wants one cloth or more of it's product (only integers allowed)
            if int(amount) != amount or amount <= 0:
                continue

            # collect and prepared all relevant details of the product and add them to the final order table
            product_info = get_product_full_details(cloths_table=home_page_table, product_id=product_id)
            product_summary = generate_summary_info(product_info=product_info, amount=int(amount))
            table.append(product_summary)

    # only if there is an actual order, get progress to order summary page
    if table:
        session['order_summary_info'] = table
        return render_template("order_summary.html", username=username, table=table)
    # otherwise go back to home page
    else:
        return redirect(url_for('home_page'))


@app.route('/admin')
def admin():
    # go back to sign in page if the username is not familiar in the session
    username = session.get('username')
    if not username:
        return render_template("sign_in.html")

    # collect products information directly from the DB
    cloths = ClothsDataCollection()
    df = cloths.admin_page_df
    table_headers, table_data = df.columns.tolist(), df.values.tolist()

    # collect the current update status (True if the user actually changed something, otherwise False)
    update_done = session.get('update_done', default=False)

    # go the admins HTML template, send all relevant variables
    return render_template(
        "admin.html", username=username, table_headers=table_headers, table_data=table_data, update_done=update_done
    )


@app.route('/admin_auth_handler')
def admin_auth_handler():
    # go back to sign in page if the username is not familiar in the session
    username = session.get('username')
    if not username:
        return render_template("sign_in.html")

    # check if the user is an admin or not
    is_admin_flag = is_admin(username)

    # let the user to move to admins' page if he is an admin
    if is_admin_flag:
        return redirect(url_for("admin"))

    # send the user back to home page if he is not an admin and let him no why he is not allowed
    error_message = "You are not authorized to access the admin page"
    return redirect(url_for('home_page', error_message=error_message))


@app.route('/save_cloths_table', methods=['POST'])
def save_cloths_table():
    # collect products information directly from the DB
    cloths = ClothsDataCollection()
    current_table = cloths.admin_page_data_to_html

    # update the DB if needed
    # return True if there was an actual update, otherwise False
    request_data: Dict = request.form
    update_done = UpdateClothsTable(request_data=request_data, current_table=current_table).run()

    # set update status in the session and go back to admins' page
    session['update_done'] = update_done
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)

