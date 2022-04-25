from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for
from flask import request
from flask import session

from application.database import DataBase


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
        password = request.form.to_dict()["password"]
        room_code = request.form.to_dict()["room_code"]
        # Check if the user was found. If they were then add the user_id to the session
        db = DataBase()
        u = db.get_user_by_credentials(username, password)
        db.close()
        if u == False: return redirect(url_for("views.login"))
        # Add the user data to the session
        session["user"] = u
        session["room_code"] = room_code if room_code != "" else "GLOBAL"
        return redirect(url_for("views.home"))
    # Handle the user navigating to the login page
    else:
        # Only display the login page if the user is not logged in. Otherwise, redirect to the home page
        if session.get("user") is None:
            return render_template("login.html")
        else:
            return redirect(url_for("views.home"))


@view.route("/logout")
def logout():
    """Logs out the user from the application by popping the user object and room code from the session 
    dictionary.

    Returns:
        None: Displays the login page for the user.
    """
    session.pop("user", None)
    session.pop("room_code", None)
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
    if session.get("user") is not None:
        return render_template("index.html")
    # Otherwise, this redirects to the login page
    else:
        return redirect(url_for("views.login"))

@view.route("/users")
def all_users():
    """Displays all user accounts for the site. This url is reserved for only superusers.

    Returns:
        None: Displays a page containing all users if the logged in user is a superuser.
    """
    # Redirect user to login page if they aren't logged in
    if session.get("user") is None:
        return redirect(url_for("views.login"))
    # Otherwise, check if they are a superuser. If they are, then display the page. Otherwise,
    # redirect them to the home page.
    else:
        # Get all users from the database if the user is a superuser
        if session.get("user").user_type == 1:
            db = DataBase()
            users = db.get_all_users()
            db.close()
            users.sort(key=lambda u: u.username)
            return render_template("users.html", users=users)
        else:
            return redirect(url_for("views.home"))