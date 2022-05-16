from flask import Blueprint
from flask import request
from flask import session

from application.database import DataBase
from application.utils import is_superuser
from application.utils import logged_in
from application.utils import claim_codes


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
@logged_in
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
@logged_in
def get_room_code():
    """Returns the room code associated with the current session. This is useful for retriving the room
    code so that messages can be organized by room.

    Returns:
        dict: A dict containing the room code
    """
    return {"room_code": session.get("room_code")}

@api.route("/get_message_by_id/<msg_id>")
def get_message_by_id(msg_id):
    """Gets a message using the message's ID.

    Args:
        msg_id (int): The unique ID of the message to find

    Returns:
        dict: A dict containing the message data or an empty dict if the message was not found
    """
    db = DataBase()
    for msg in db.get_all_messages():
        if msg.msg_id == int(msg_id):
            return msg.to_dict()
    else:
        return {}