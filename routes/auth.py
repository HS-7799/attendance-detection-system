import json
from flask import Flask, url_for, render_template, request, redirect, session, Blueprint
from services.models import db, User, Role
from oauthlib.oauth2 import WebApplicationClient
import requests
import os
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
auth = Blueprint("auth", __name__, template_folder="templates")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CLIENT_ID = '606086608167-6aalo80s9u8hh9kfo78abi7rgs6m263m.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'MBopOywNKl5PX4V3Tng4um6K'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@auth.record_once
def on_load(state):
    login_manager.init_app(state.app)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@auth.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
        # hd="uit.ac.ma"
    )
    return redirect(request_uri)


@auth.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        # unique_id = userinfo_response.json()["sub"]
        user_email = userinfo_response.json()["email"]
        # picture = userinfo_response.json()["picture"]
        # users_name = userinfo_response.json()["given_name"]
    else:
        return render_template("index.html",
                               error=False,
                               error_message='User email not available or not verified by Google.',
                               error_number='400')
    user = User.query.filter_by(email=user_email).first()
    # Doesn't exist? show error
    if not user:
        return render_template("error.html", name='ENSAKISTE', error=401)

    # Begin user session by logging the user in
    login_user(user)
    if (user.roles[0].id == 1):
        return redirect("/admin")
    if (user.roles[0].id == 4):
        return redirect("/student")
    # Send user back to his dashboard


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

