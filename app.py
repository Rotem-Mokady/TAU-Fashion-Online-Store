from flask import Flask, redirect, render_template, request, url_for, session
import os

from auth_and_register import (
    signing_in_response, validate_email_template, validate_username_template, validate_password_template,
    ensure_new_user, register_new_user, is_admin
)
from cloths_handler import ClothsHandler

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

    return render_template("home_page.html", username=username, table=table)


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

