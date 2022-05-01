from flask_session import Session
from flask_socketio import SocketIO
from flask_socketio import emit
from flask import session
from numpy import broadcast

from config import Config
from application.database import DataBase
from application.message import Message
from application import create_app
from application.utils import public_rooms


# Create the app and set the secret key
app = create_app()
app.secret_key = Config.SECRET_KEY

# Configure the session
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configure the socket interface
socketio = SocketIO(app)


# Socket events


@socketio.on('client connected')
def on_connect():
    """Sends all messages from the database with the same room code as the client to the client 
    on connection."""
    db = DataBase()
    messages = db.get_room_messages(session.get("room_code"))
    db.close()
    # Convert message objects to json
    message_data = []
    for m in messages:
        message_data.append(m.to_dict())
    emit('after connection', {'messages': message_data, 'public_rooms': public_rooms})

@socketio.on('send message')
def on_message_send(data, methods=["POST"]):
    """Handles socket connections related to when a user sends a message. The message is
    added to the database and then broadcast to all connected clients. The client will 
    check whether the room code matches the client's room code and then display the message
    if it does.

    Args:
        data (dict): The message data that is generated when a user sends a message.
    """
    data = dict(data)
    m = Message(data["content"], data["author_id"], data["author_username"], data["room_code"])
    db = DataBase()
    db.add_message(m)
    db.close()
    emit('new message', m.to_dict(), broadcast=True)

@socketio.on('room status update')
def on_room_status_update(data, methods=["POST"]):
    """Handles socket connections related to when the status of a public room changes. This can
    be when the room is changed from public to private or vice versa. 

    Args:
        data (dict): The room status data containing the new room status.
    """
    data = dict(data)
    if data["action"] == "Public" and data["room_code"] not in public_rooms:
        public_rooms.append(data["room_code"])
    elif data["action"] == "Private" and data["room_code"] in public_rooms:
        public_rooms.remove(data["room_code"])
    emit('room status changed', data, broadcast=True)

@socketio.on('on message delete')
def on_message_delete(data, methods=["POST"]):
    """Handles socket connections to delete messages from the database. This route then broadcasts
    a message deleted event to all connected clients, who then handle the deletion of the message 
    from the screens of their users.

    Args:
        data (dict): Data containing the msg_id of the message to be deleted.
    """
    data = dict(data)
    db = DataBase()
    db.delete_message(data["msg_id"])
    emit("message deleted", data, broadcast=True)


# Mainline
if __name__ == "__main__":
    socketio.run(app, debug=Config.DEBUG, host=Config.SERVER)