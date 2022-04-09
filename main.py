# https://github.com/techwithtim/Chat-Web-App/tree/master/

from flask_session import Session
from flask_socketio import SocketIO
from flask_socketio import emit

from config import Config
from application.database import DataBase
from application.message import Message
from application import create_app


# Create the app and set the secret key
app = create_app()
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Configure the session
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configure the socket interface
socketio = SocketIO(app)


# Socket events


@socketio.on('client connected')
def on_connect():
    """Sends all messages from the database to the client on connection."""
    db = DataBase()
    messages = db.get_all_messages()
    # Convert message objects to json
    message_data = []
    for m in messages:
        message_data.append(m.to_dict())
    emit('after connection', {'data': message_data})

@socketio.on('send message')
def on_message_send(data, methods=["POST"]):
    """Handles socket connections related to when a user sends a message. The message is
    added to the database and then broadcast to all connected clients.

    Args:
        data (dict): The message data that is generated when a user sends a message.
    """
    data = dict(data)
    m = Message(data["content"], data["author_username"])
    db = DataBase()
    db.add_message(m)
    emit('new message', m.to_dict(), broadcast=True)

# Mainline
if __name__ == "__main__":
    socketio.run(app, debug=Config.DEBUG, host=Config.SERVER)