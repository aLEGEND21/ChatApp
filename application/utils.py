import functools
import json
from flask import redirect
from flask import url_for
from flask import session


# DECORATORS

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


# FUNCTIONS

def get_all_emojis():
    """Gets all emojis from the JSON file containing the emojis and returns them. The emojis are
    formatted as {emoji_name: emoji}.

    Returns:
        dict: A dict of all emojis with the emoji name as the key and the emoji as the value.
    """
    # Note: Similar emojis have been removed from the json file such as emojis with different skin tones
    # Note: The emoji file was sourced from: https://github.com/ArkinSolomon/discord-emoji-converter/blob/master/emojis.json
    with open("./emojis.json", 'rb') as f:
        emojis = json.load(f)
    return emojis



# VARIABLES

claim_codes = [] # Contains all active claim codes in the application
public_rooms = [] # Contains the room codes for all the public rooms in the application