import sqlite3
import copy

from .message import Message
from .user import User


class DataBase:

    def __init__(self, db_path="database.db"):
        """Attempt to create a connection to the database via the provided path. Additionally,
        the cursor from the connection is saved.

        Args:
            db_path (str, optional): The path to the database. Defaults to "messages.db".
        """
        try:
            self.conn = sqlite3.connect(db_path)
        except Exception as e:
            print(e)
        else:
            self.cursor = self.conn.cursor()
            self._create_users_table()
            self._create_messages_table()
    
    def _create_users_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS Users
                (username TEXT, password TEXT, user_type INTEGER, user_id INTEGER PRIMARY KEY)"""
        self.cursor.execute(query)
        self.conn.commit()
    
    def _create_messages_table(self):
        """Create the table containing all messages in the database. If the table already exists,
        then do not create the table.
        """
        query = f"""CREATE TABLE IF NOT EXISTS Messages 
                (content TEXT, author_id INTEGER, author_username TEXT, timestamp Date, room_code TEXT, id INTEGER PRIMARY KEY)"""
        self.cursor.execute(query)
        self.conn.commit()
    
    def close(self):
        """Closes the database connection. This should be run once the database instance is
        no longer needed.
        """
        self.conn.close()
    
    def add_user(self, user_object: User):
        query = """INSERT INTO Users(username, password, user_type, user_id) VALUES (?,?,?,?)"""
        self.cursor.execute(query, (user_object.username, user_object.password, user_object.user_type, user_object.user_id))
        self.conn.commit()
    
    def get_user_by_id(self, user_id):
        # Make the query to get the user from the database
        query = """SELECT * FROM Users WHERE user_id = ?"""
        user_tuples = self.cursor.execute(query, (str(user_id),)).fetchall()
        
        # Check if the user was found
        if len(user_tuples) == 0:
            return False
        else:
            user_tuple = user_tuples[0]

        # Construct the user object using the user tuple data
        u = User(
            user_tuple[0],
            user_tuple[1],
            user_tuple[2],
            user_tuple[3]
        )

        return u
    
    def get_user_by_credentials(self, username: str, password: str):
        # Make the query to get the user from the database
        query = """SELECT * FROM Users WHERE username = ? AND password = ?"""
        user_tuples = self.cursor.execute(query, (username, password)).fetchall()
        
        # Check if the user was found
        if len(user_tuples) == 0:
            return False
        else:
            user_tuple = user_tuples[0]

        # Construct the user object using the user tuple data
        u = User(
            user_tuple[0],
            user_tuple[1],
            user_tuple[2],
            user_tuple[3]
        )

        return u
    
    def add_message(self, msg_object: Message):
        query = """INSERT INTO Messages(content, author_id, author_username, timestamp, room_code, id)
                VALUES (?,?,?,?,?,?)"""
        self.cursor.execute(query, (msg_object.content, msg_object.author_id, msg_object.author_username, msg_object.timestamp, msg_object.room_code, msg_object.msg_id))
        self.conn.commit()
    
    def get_all_messages(self):
        """Gets all messages from the message database.

        Returns:
            list[Message]: A list of Message objects containing the message data from the database.
        """
        # Make the query to fetch all messages from the Messages table
        query = """SELECT * FROM Messages"""
        self.cursor.execute(query)
        message_tuples = self.cursor.fetchall()
        
        # Construct the Message objects from the tuple data
        messages = []
        for msg in message_tuples:
            m = Message.construct_message(msg[0], msg[1], msg[2], msg[3], msg[4], msg[5])
            messages.append(m)
        
        # Sort the messages from old -> new
        messages.sort(key=lambda m: m.timestamp)

        return messages
    
    def get_room_messages(self, room_code="GLOBAL"):
        """Gets all messages sent in the specified chat room from the database and returns them.

        Args:
            room_code (str, optional): The code of the chat room. Defaults to "GLOBAL".
        
        Returns:
            list[Message]: A list of Message objects that were sent in the chat room with the specified
                room code.
        """
        # Make the query to fetch all messages from the Messages table
        query = """SELECT * FROM Messages"""
        self.cursor.execute(query)
        message_tuples = self.cursor.fetchall()

        # Remove the messages that are not from the correct room
        for msg in copy.copy(message_tuples):
            if msg[4] != room_code:
                message_tuples.remove(msg)
        
        # Construct the Message objects from the remaining tuple data
        messages = []
        for msg in message_tuples:
            m = Message.construct_message(msg[0], msg[1], msg[2], msg[3], msg[4], msg[5])
            messages.append(m)
        
        # Sort the messages from old -> new
        messages.sort(key=lambda m: m.timestamp)

        return messages