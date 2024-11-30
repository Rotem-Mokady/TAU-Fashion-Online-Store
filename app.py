from flask import Flask, redirect, render_template, request, url_for, session
import os
from typing import Dict

from auth_and_register import (
    signing_in_response, validate_email_template, validate_username_template, validate_password_template,
    ensure_new_user, register_new_user, is_admin
)
from cloths_handler import (
    ClothsHandler, get_cloth_full_details, generate_summary_info, add_transaction_to_db, UpdateClothsTable
)

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def sign_in():
    if session.get('username'):
        return redirect(url_for("home_page"))

    return render_template("sign_in.html")


@app.route('/sign_in', methods=['POST'])
def sign_in_auth_handler():
    username, password = request.form['username'], request.form['password']
    resp = signing_in_response(username=username, password=password)

    if resp:
        session['username'] = username  # store username in session
        return redirect(url_for("home_page"))

    error_message = "Invalid username or password. Please try again."
    return render_template("sign_in.html", error_message=error_message)


@app.route('/sign_up')
def sign_up():
    return render_template("sign_up.html")


@app.route('/sign_up_handler', methods=['POST'])
def sign_up_registration_handler():
    email, username = request.form['email'], request.form['username']
    password, confirmed_password = request.form['password'], request.form['confirm_password']

    email_resp = validate_email_template(email)
    username_resp = validate_username_template(username)
    password_resp = validate_password_template(password)
    is_new = ensure_new_user(email=email, username=username)

    if not (email_resp and username_resp and password_resp):
        error_message = "Invalid email address, username or password. Please try again."
        return render_template("sign_up.html", error_message=error_message)

    elif password != confirmed_password:
        error_message = "Two different passwords entered. Please try again."
        return render_template("sign_up.html", error_message=error_message)

    elif not is_new:
        error_message = "Email or username is already in use."
        return render_template("sign_up.html", error_message=error_message)

    register_new_user(request_data=request.form)
    session['username'] = username  # store username in session
    return redirect(url_for("home_page"))


@app.route('/home_page')
def home_page():
    username = session.get('username')
    if not username:
        return render_template("sign_in.html")

    if not session.get('home_page_table'):
        cloths = ClothsHandler()
        table = cloths.home_page_data_to_html
        session['home_page_table'] = table
    else:
        table = session['home_page_table']

    order_summary_success_message = request.args.get('success_message', default=None)
    order_summary_info = session.get('order_summary_info', default=None)

    # If the user accepted and he has a reservation
    if order_summary_success_message and order_summary_info:
        session['order_summary_info'] = None
        add_transaction_to_db(username=username, data=order_summary_info)

    not_admin_message_error = request.args.get('error_message', default=None)

    return render_template(
        "home_page.html", username=username, table=table,
        success_message=order_summary_success_message, error_message=not_admin_message_error
    )


@app.route('/order_summary', methods=['GET', 'POST'])
def order_summary():
    username, home_page_table = session.get('username'), session.get('home_page_table')

    if not username or not home_page_table:
        return redirect(url_for('home_page'))

    table = []

    for key in request.form:
        if key.startswith('product_'):
            # Extract the product ID and the new order value
            product_id = int(key.split('_')[1])
            amount = int(request.form[key])

            if amount > 0:
                product_info = get_cloth_full_details(cloths_table=home_page_table, product_id=product_id)
                product_summary = generate_summary_info(product_info=product_info, amount=amount)
                table.append(product_summary)

    if table:
        session['order_summary_info'] = table
        return render_template("order_summary.html", username=username, table=table)
    else:
        return redirect(url_for('home_page'))


@app.route('/admin')
def admin():
    username = session.get('username')
    if not username:
        render_template("sign_in.html")

    cloths = ClothsHandler()
    df = cloths.admin_page_df
    table_headers, table_data = df.columns.tolist(), df.values.tolist()

    update_done = session.get('update_done', default=False)

    return render_template(
        "admin.html", username=username, table_headers=table_headers, table_data=table_data, update_done=update_done
    )


@app.route('/admin_auth_handler')
def admin_auth_handler():
    username = session.get('username')
    if not username:
        render_template("sign_in.html")

    is_admin_flag = is_admin(username)

    if is_admin_flag:
        return redirect(url_for("admin"))

    error_message = "You are not authorized to access the admin page"
    return redirect(url_for('home_page', error_message=error_message))


@app.route('/save_cloths_table', methods=['POST'])
def save_cloths_table():
    cloths = ClothsHandler()
    current_table = cloths.admin_page_data_to_html

    request_data: Dict = request.form
    update_done = UpdateClothsTable(request_data=request_data, current_table=current_table).run()

    session['update_done'] = update_done
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)

