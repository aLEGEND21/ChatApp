from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for
from flask import request
from flask import session

from application.database import DataBase
from application.utils import logged_in


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
@logged_in
def home():
    """Displays the main page for the site. This allows the user to send and recieve messages with
    others who are using the site as well.

    Returns:
        None: Displays the main/home page of the site if the user is logged in.
    """
    return render_template("index.html")

@view.route("/users")
@logged_in
def all_users():
    """Displays all user accounts for the site. This url is reserved for only superusers.

    Returns:
        None: Displays a page containing all users if the logged in user is a superuser.
    """
    # Get all users from the database if the user is a superuser
    if session.get("user").user_type == 1:
        db = DataBase()
        users = db.get_all_users()
        db.close()
        users.sort(key=lambda u: u.username)
        return render_template("users.html", users=users)
    # Redirect the user home if they are not a superuser
    else:
        return redirect(url_for("views.home"))