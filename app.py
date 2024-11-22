from flask import Flask, redirect, render_template, request, url_for

from auth_and_register import (
    signing_in_response, validate_email_template, validate_username_template, validate_password_template,
    ensure_new_user, register_new_user, is_admin
)

app = Flask(__name__)


# @app.errorhandler(404)
# def invalid_route(e):
#     return redirect("http://127.0.0.1:5000/")


@app.route('/')
def sign_in():
    return render_template("sign_in.html")


@app.route('/sign_in', methods=['POST'])
def sign_in_auth_handler():
    username, password = request.form['username'], request.form['password']
    resp = signing_in_response(username=username, password=password)

    if resp:
        return redirect(url_for("home_page", username=username))

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

    register_new_user()
    return redirect(url_for("home_page", username=username))


@app.route('/home_page')
def home_page():
    username = request.args.get('username')
    return f"Hi {username}! Welcome to TAUFashion Online Store!"


@app.route('/admins_only')
def admins_only():
    username = request.args.get('username')
    return f"Hello admin {username}!"


@app.route('/admins_only_auth_handler', methods=['POST'])
def admins_only_auth_handler():
    username = request.args.get('username')
    is_admin_flag = is_admin()

    if is_admin_flag:
        return redirect(url_for("admins_only", username=username))

    return redirect(url_for("home_page", username=username))


if __name__ == "__main__":
    app.run(debug=True)

