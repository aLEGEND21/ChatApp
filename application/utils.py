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