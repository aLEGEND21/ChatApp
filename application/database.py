import sqlite3
import copy
import pymongo
import replit
import requests
import ssl

from config import Config
from .message import Message
from .user import User


class DataBase:

    def __init__(self):
        self.client = pymongo.MongoClient(Config.DB_CONNECTION_STRING, ssl_cert_reqs=ssl.CERT_NONE)
        self.db = self.client["ChatApp"]
        self.users = self.db["Users"]
        self.messages = self.db["Messages"]
    
    def close(self):
        pass

    def add_user(self, user_object: User):
        # Convert the user_object to JSON
        user_dict = user_object.to_dict()
        user_dict["_id"] = user_dict.pop("user_id")

        # Update the users collection with the new user object
        self.users.insert_one(user_dict)
    
    def get_all_users(self):
        """Gets all users from the database and converts them into User objects.

        Returns:
            list[User]: A list of all users registered in the site
        """
        # Query the database for all the user data and convert it into User objects
        user_objects = []
        for user_dict in self.users.find():
            user_objects.append(
                User(
                    user_dict["username"],
                    user_dict["password"],
                    user_dict["user_type"],
                    user_dict["_id"]
                )
            )
        
        return user_objects

    def get_user_by_id(self, user_id):
        # Make the query to the database
        user_data = self.users.find_one({"_id": user_id})
        
        # Check if the user was found
        if user_data is None:
            return False
        
        # Construct the user object using the user_data
        user_object = User(
            user_data["username"],
            user_data["password"],
            user_data["user_type"],
            user_data["_id"]
        )

        return user_object
    
    def get_user_by_credentials(self, username: str, password: str):
        # Make the query to the database
        user_data = self.users.find_one({"username" : username, "password": password})
        
        # Check if the user was found
        if user_data is None:
            return False
        
        # Construct the user object using the user_data
        user_object = User(
            user_data["username"],
            user_data["password"],
            user_data["user_type"],
            user_data["_id"]
        )

        return user_object
    
    def add_message(self, msg_object: Message):
        # Format the message object data into JSON
        msg_dict = {
            "content": msg_object.content,
            "author_id": msg_object.author_id,
            "author_username": msg_object.author_username,
            "timestamp": msg_object.timestamp,
            "_id": msg_object.msg_id,
            "room_code": msg_object.room_code,
            "replying_to": msg_object.replying_to
        }

        # Make the query to the database
        self.messages.insert_one(msg_dict)
    
    def get_all_messages(self):
        """Gets all messages from the message database.

        Returns:
            list[Message]: A list of Message objects containing the message data from the database.
        """
        message_data = self.messages.find()
        
        # Check if there were any messages in the database
        if message_data is None:
            return []
        
        # Construct the Message objects from the message dict
        messages = []
        for msg in message_data:
            m = Message.construct_message(
                msg["content"],
                msg["author_id"],
                msg["author_username"],
                msg["timestamp"],
                msg["room_code"],
                msg["_id"],
                msg["replying_to"]
            )
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
        message_data = self.messages.find()
        
        # Check if there were any messages in the database
        if message_data is None:
            return []

        # Construct the Message objects from the message dict
        messages = []
        for msg in message_data:
            # Skip over all messages that are not from the specified room
            if msg["room_code"] != room_code:
                continue
            m = Message.construct_message(
                msg["content"],
                msg["author_id"],
                msg["author_username"],
                msg["timestamp"],
                msg["room_code"],
                msg["_id"],
                msg["replying_to"]
            )
            messages.append(m)
        
        # Sort the messages from old -> new
        messages.sort(key=lambda m: m.timestamp)

        return messages
    
    def get_message(self, msg_id: int):
        """Retrieves a message from the database and converts it to a Message object

        Args:
            msg_id (int): The unique id of the message you wish to get

        Returns:
            Message: The Message object containing the message data
        """
        m = self.messages.find_one({"_id": msg_id})
        if m is None:
            return None
        else:
            return Message(
                m["content"],
                m["author_id"],
                m["author_username"],
                m["room_code"],
                m["replying_to"]
            )

    def delete_all_messages(self):
        """Removes all messages from the Messages collection in the database.
        """
        self.messages.delete_many({})
    
    def delete_message(self, msg_id: int):
        """Deletes the specified message from the Messages collection.

        Args:
            msg_id (int): The unique id of the message to be deleted
        """
        self.messages.delete_one({"_id": int(msg_id)})
    
    def edit_message(self, msg_id: int, new_content: str):
        """Edits the specified message from the Messages collection.
        
        Args:
            msg_id (int): The unique id of the message to be edited
            new_content (str): The new content of the message which will replace the existing content
        """
        self.messages.update_one({"_id": int(msg_id)}, {"$set": {"content": new_content}})


class ReplitDataBase:

    def __init__(self):
        self.db_url = requests.get(Config.SITE_URL + "/api/get_database_url").json()["db_url"]
        self.db = replit.Database(self.db_url)
    
    @property
    def users(self):
        return self.db["Users"]
    
    @property
    def messages(self):
        return self.db["Messages"]

    def close(self):
        pass

    def add_user(self, user_object: User):
        # Convert the user_object to JSON
        user_dict = user_object.to_dict()
        user_dict["_id"] = user_dict.pop("user_id")

        # Update the users list with the new user object
        self.users.append(user_dict)
    
    def get_all_users(self):
        """Gets all users from the database and converts them into User objects.

        Returns:
            list[User]: A list of all users registered in the site
        """
        # Query the database for all the user data and convert it into User objects
        user_objects = []
        for user_dict in self.users:
            user_objects.append(
                User(
                    user_dict["username"],
                    user_dict["password"],
                    user_dict["user_type"],
                    user_dict["_id"]
                )
            )
        
        return user_objects

    def get_user_by_id(self, user_id):
        # Make the query to the database
        for user_data in self.users:
            if int(user_data["_id"]) == user_id:
                break
        else:
            return False
        
        # Construct the user object using the user_data
        user_object = User(
            user_data["username"],
            user_data["password"],
            user_data["user_type"],
            user_data["_id"]
        )

        return user_object
    
    def get_user_by_credentials(self, username: str, password: str):
        # Compare the username and password to the credentials of the users in the database
        for user_data in self.users:
            if user_data["username"] == username and user_data["password"] == password:
                break
        else:
            return False
        
        # Construct the user object using the user_data
        user_object = User(
            user_data["username"],
            user_data["password"],
            user_data["user_type"],
            user_data["_id"]
        )

        return user_object
    
    def add_message(self, msg_object: Message):
        # Format the message object data into JSON
        msg_dict = {
            "content": msg_object.content,
            "author_id": msg_object.author_id,
            "author_username": msg_object.author_username,
            "timestamp": str(msg_object.timestamp),
            "_id": msg_object.msg_id,
            "room_code": msg_object.room_code,
            "replying_to": msg_object.replying_to
        }

        # Make the query to the database
        self.messages[msg_object.msg_id] = msg_dict
    
    def get_message(self, msg_id: int):
        msg = self.messages.get(int(msg_id))
        if msg is None:
            return {}
        else:
            return Message.construct_message(
                    msg["content"],
                    msg["author_id"],
                    msg["author_username"],
                    msg["timestamp"],
                    msg["room_code"],
                    msg["_id"],
                    msg["replying_to"]
                )
    
    def get_all_messages(self):
        """Gets all messages from the message database.

        Returns:
            list[Message]: A list of Message objects containing the message data from the database.
        """        
        # Construct the Message objects from the message dict
        messages = []
        for msg_id in self.messages:
            msg = self.messages[msg_id]
            m = Message.construct_message(
                msg["content"],
                msg["author_id"],
                msg["author_username"],
                msg["timestamp"],
                msg["room_code"],
                msg["_id"],
                msg["replying_to"]
            )
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
        # Construct the Message objects from the message dict
        messages = []
        for msg_id in self.messages:
            msg = self.messages[msg_id]
            # Skip over all messages that are not from the specified room
            if msg["room_code"] != room_code:
                continue
            m = Message.construct_message(
                msg["content"],
                msg["author_id"],
                msg["author_username"],
                msg["timestamp"],
                msg["room_code"],
                msg["_id"],
                msg["replying_to"]
            )
            messages.append(m)
        
        # Sort the messages from old -> new
        messages.sort(key=lambda m: m.timestamp)

        return messages
    
    def delete_all_messages(self):
        """Removes all messages from the Messages list in the database.
        """
        for msg_id in self.messages:
            del self.messages[msg_id]
    
    def delete_message(self, msg_id: int):
        """Deletes the specified message from the Messages list.

        Args:
            msg_id (int): The unique id of the message to be deleted
        """
        del self.messages[str(msg_id)]
    
    def edit_message(self, msg_id: int, new_content: str):
        """Edits the specified message from the Messages list.
        
        Args:
            msg_id (int): The unique id of the message to be edited
            new_content (str): The new content of the message which will replace the existing content
        """
        edited_message = self.messages[int(msg_id)]
        edited_message["content"] = new_content
        self.messages[int(msg_id)] = edited_message


class SQLiteDataBase:

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
                (content TEXT, author_id INTEGER, author_username TEXT, timestamp Date, room_code TEXT, msg_id INTEGER PRIMARY KEY)"""
        self.cursor.execute(query)
        self.conn.commit()
    
    def perform_query(self, query, args=[]):
        """Performs the specified query. When using this function, make sure that the input query
        is trusted as it is input directly into the database.

        Args:
            query (str): The sqlite query you wish to perform

        Returns:
            sqlite3.Cursor: The cursor object containing the result of the query
        """
        res = self.cursor.execute(query, args)
        self.conn.commit()
        return res
    
    def close(self):
        """Closes the database connection. This should be run once the database instance is
        no longer needed.
        """
        self.conn.close()
    
    def add_user(self, user_object: User):
        query = """INSERT INTO Users(username, password, user_type, user_id) VALUES (?,?,?,?)"""
        self.cursor.execute(query, (user_object.username, user_object.password, user_object.user_type, user_object.user_id))
        self.conn.commit()
    
    def get_all_users(self):
        """Gets all users from the database and converts them into User objects.

        Returns:
            list[User]: A list of all users registered in the site
        """
        # Make the query to get all users from the database
        query = """SELECT * FROM Users"""
        all_users = self.cursor.execute(query)
        
        # Convert the user tuples into User objects
        user_objects: list[User] = []
        for user_tuple in all_users:
            user_objects.append(
                User(
                    user_tuple[0],
                    user_tuple[1],
                    user_tuple[2],
                    user_tuple[3]
                )
            )
        
        return user_objects

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
        query = """INSERT INTO Messages(content, author_id, author_username, timestamp, room_code, msg_id)
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
            m = Message.construct_message(msg[0], msg[1], msg[2], msg[3], msg[4], msg[5], msg[6])
            messages.append(m)
        
        # Sort the messages from old -> new
        messages.sort(key=lambda m: m.timestamp)

        return messages
    
    def delete_all_messages(self):
        """Removes all messages from the Messages table. This preserves all tables in the database and
        only deletes the content from the Messages table.
        """
        query = """DELETE FROM Messages"""
        self.cursor.execute(query)
        self.conn.commit()
    
    def delete_message(self, msg_id: int):
        """Deletes the specified message from the Messages table.

        Args:
            msg_id (int): The unique id of the message to be deleted
        """
        query = """DELETE FROM Messages WHERE msg_id = ?"""
        self.cursor.execute(query, (msg_id,))
        self.conn.commit()
    
    def edit_message(self, msg_id: int, new_content: str):
        """Edits the specified message from the Messages table.
        
        Args:
            msg_id (int): The unique id of the message to be edited
            new_content (str): The new content of the message which will replace the existing content
        """
        query = """UPDATE Messages SET content = ? WHERE msg_id = ?"""
        self.cursor.execute(query, (new_content, msg_id))
        self.conn.commit()