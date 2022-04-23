from flask import Blueprint
from flask import request
from flask import session

from application.database import DataBase


api = Blueprint("api", __name__)


# Routes


# DEPRECATED
'''@view.route("/get_username")
def get_username():
    """Returns the username associated with the current session. This can be used by the socket in order
    to get the client's username.

    Returns:
        dict: A dict containing the user's username
    """
    return {"username": session.get("username")}'''

@api.route("/get_user")
def get_user():
    """Returns the json user data that is associated with the current session. The data will contain the
    user's username and other information.

    Returns:
        dict: A dict containing the user data
    """
    db = DataBase()
    u = db.get_user_by_id(session.get("user").user_id)
    u_dict = u.to_dict()
    u_dict.pop("password")
    return u_dict

@api.route("/get_room_code")
def get_room_code():
    """Returns the room code associated with the current session. This is useful for retriving the room
    code so that messages can be organized by room.

    Returns:
        dict: A dict containing the room code
    """
    return {"room_code": session.get("room_code")}