from flask import Flask, redirect, render_template, request, url_for, session
import os
from ast import literal_eval

from auth_and_register import (
    signing_in_response, validate_email_template, validate_username_template, validate_password_template,
    ensure_new_user, register_new_user, is_admin
)
from cloths_handler import ClothsHandler, get_cloth_full_details, generate_summary_info, add_transaction_to_db

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def sign_in():
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

    cloths = ClothsHandler()
    table = cloths.home_page_data_to_html
    session['home_page_table'] = table

    order_summary_success_message = request.args.get('success_message', default=None)
    order_summary_info = request.args.get('order_summary_info', default=None)

    # If the user accepted and he has a reservation
    if order_summary_success_message and order_summary_info:
        success_message, data = order_summary_success_message, literal_eval(order_summary_info)
        request.args['success_message'], request.args['order_summary_info'] = None, None

        add_transaction_to_db(data=data)

    return render_template(
        "home_page.html", username=username, table=table, success_message=order_summary_success_message
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
                product_info = get_cloth_full_details(cloth_table=home_page_table, product_id=product_id)
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

    return render_template("admin.html", username=username)


@app.route('/admin_auth_handler')
def admin_auth_handler():
    username = session.get('username')
    if not username:
        render_template("sign_in.html")

    is_admin_flag = is_admin(username)

    if is_admin_flag:
        return redirect(url_for("admin"))

    error_message = "You are not authorized to access the admin page"
    cloth_df = home_page_handler()
    
    return render_template("home_page.html", username=username, error_message=error_message, table=cloth_df)


if __name__ == "__main__":
    app.run(debug=True)

