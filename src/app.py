from flask import Flask, render_template, request, make_response, redirect, url_for


USERNAME_COOKIE_NAME = "username"
DEFAULT_USERNAME = "guest"


app = Flask(__name__)


@app.route("/")
def render_homepage():
    username = "guest"
    if USERNAME_COOKIE_NAME in request.cookies:
        username = request.cookies.get(USERNAME_COOKIE_NAME)
    return render_template('homepage.html', **locals())


@app.route('/setcookie', methods=['POST'])
def set_username_cookie():
    username = request.form[USERNAME_COOKIE_NAME]
    resp = make_response(redirect(url_for("render_homepage")))
    resp.set_cookie(USERNAME_COOKIE_NAME, username)

    return resp
