import functools
from flask import redirect
from flask import url_for
from flask import session


def logged_in(func):
    """Checks whether the user is logged in to the application by checking if there is a valid
    user key in the session dict. If there is not, then the user is redirected to the login
    page of the application.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("user") is None:
            return redirect(url_for("views.login"))
        else:
            return func(*args, **kwargs)
    return wrapper

def is_superuser(func):
    """Checks whether the user is a superuser before allowing them to access the url route. If 
    they are not a superuser, they are redirected back to the home page.
    """
    @functools.wraps(func)
    @logged_in
    def wrapper(*args, **kwargs):
        if session.get("user").user_type != 1:
            return redirect(url_for("views.home"))
        else:
            return func(*args, **kwargs)
    return wrapper


# Variables
claim_codes = [] # Contains all active claim codes in the application
public_rooms = [] # Contains the room codes for all the public rooms in the application