from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for
from flask import request
from flask import session


# Create the blueprint
view = Blueprint("views", __name__)


# Routes


@view.route("/login", methods=["GET", "POST"])
def login():
    """Logs the user into the website. If a GET request is made, the login page is displayed to
    the user. If a POST request is made, then the user is logged in using the data in the form
    recieved in the POST request.

    Returns:
        None: Displays the login page or redirects to the home page.
    """
    # Handle internal request containing the user input from the login page
    if request.method == "POST":
        username = request.form.to_dict()["username"]
        session["username"] = username # Save the username from the request form to the session var
        return redirect(url_for("views.home"))
    # Handle the user navigating to the login page
    else:
        # Only display the login page if the user is not logged in. Otherwise, redirect to the home page
        if session.get("username") is None:
            return render_template("login.html")
        else:
            return redirect(url_for("views.home"))


@view.route("/logout")
def logout():
    """Logs out the user from the application by popping the username from the session dictionary.

    Returns:
        None: Displays the login page for the user.
    """
    session.pop("username", None)
    return redirect(url_for("views.login"))


@view.route("/")
@view.route("/home")
def home():
    """Displays the main page for the site. This allows the user to send and recieve messages with
    others who are using the site as well.

    Returns:
        None: Displays the main/home page of the site or redirects to the login page if the user is
            not logged in.
    """
    # Display the home page if the user's username is in the session dict
    if session.get("username") is not None:
        return render_template("index.html")
    # Otherwise, this redirects to the login page
    else:
        return redirect(url_for("views.login"))


# API


@view.route("/api/get_username")
def get_username():
    """Returns the username associated with the current session. This can be used by the socket in order
    to get the client's username.

    Returns:
        dict: A dict containing the user's username
    """
    return {"username": session.get("username")}