from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask import request
from flask import session

from application.database import DataBase
from application.user import User
from application.utils import is_superuser
from application.utils import logged_in
from application.utils import claim_codes


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
        # Tell the user if they entered the wrong login credentials
        if u == False: 
            flash("Incorrect Login Credentials", "failure")
            return redirect(url_for("views.login"))
        # Add the user data to the session
        session["user"] = u
        session["room_code"] = room_code if room_code != "" else "GLOBAL"
        flash("Successfully Logged In", "success")
        return redirect(url_for("views.home", room_code=room_code))
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
    flash("Logged Out Successfully", "success")
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
    # Get the room code from the request args and reformat it
    room_code = request.args.get("room_code")
    if room_code == None:
        return redirect("/?room_code=GLOBAL")
    elif room_code == "":
        room_code = "GLOBAL"
    session["room_code"] = room_code
    return render_template("index.html")

@view.route("/users")
@is_superuser
def all_users():
    """Displays all user accounts for the site. This url is reserved for only superusers.

    Returns:
        None: Displays a page containing all users if the logged in user is a superuser.
    """
    db = DataBase()
    users = db.get_all_users()
    db.close()
    users.sort(key=lambda u: u.username)
    return render_template("users.html", users=users)

@view.route("/create_claim_code", methods=["GET", "POST"])
@is_superuser
def create_claim_code():
    if request.method == "POST":
        # Extract the data from the request form and add it to the claim_codes list
        data = request.form.to_dict()
        new_claim_code = data["claim_code"]
        recipient_username = data["recipient_username"]
        claim_codes.append(
            {
                "claim_code": new_claim_code,
                "username": recipient_username
            }
        )
        flash("Successfully created claim code for " + recipient_username, "success")
        return redirect(url_for("views.home"))
    else:
        return render_template("claim.html", superuser=True)

@view.route("/claim_account", methods=["GET", "POST"])
def claim_account():
    if request.method == "POST":
        # Extract the claim code data from the request dict
        data = request.form.to_dict()
        code = data["claim_code"]
        password = data["password"]
        confirm_password = data["confirm_password"]
        # Check if the claim code is valid
        for code_data in claim_codes:
            if code_data["claim_code"] == code:
                break
        else:
            flash("Invalid Claim Code", "failure")
            return render_template("claim.html")
        # Check if the passwords match
        if password != confirm_password: 
            flash("Passwords Do Not Match", "failure")
            return render_template("claim.html")
        # Create the account and add it to the database
        u = User(code_data["username"], password, 0)
        db = DataBase()
        db.add_user(u)
        db.close()
        claim_codes.remove(code_data) # Delete the claim code
        flash(f"Successfully claimed account for {u.username}. Please log in using {u.username} as your username", "success")
        return redirect(url_for("views.home"))
    else:
        # Prevent people from claiming an account if they are logged in
        if session.get("user") is not None:
            return redirect(url_for("views.home"))
        else:
            return render_template("claim.html")