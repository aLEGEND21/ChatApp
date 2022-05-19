import random
import time

from .message import Message


class User:

    def __init__(self, username: str, password: str, user_type: int = 0, user_id: int = None):#, messages: list[Message] = []):
        self.username = username
        self.password = password
        self.user_type = user_type # 0 is normal and 1 is superuser
        self.user_id = user_id
        #self.messages = messages

        # Generate the user id if it is not provided
        if self.user_id is None:
            time_created = round(time.time())
            self.user_id = str(time_created) + str(random.randint(1000, 9999))
        self.user_id = int(self.user_id)
    
    def to_dict(self):
        """Convert the user object into a dictionary so that it can be sent through the socket or 
        stored in the database.

        Returns:
            dict: A dict containing all user data
        """
        # Convert all messages from message objects to dicts
        """messages = []
        [messages.append(m.to_dict()) for m in self.messages]"""

        return {
            "username": self.username,
            "password": self.password,
            #"messages": messages,
            "user_type": self.user_type,
            "user_id": self.user_id
        }
    
    '''def add_message(self, message_content: str, room_code: str):
        """Adds a new message to the user's list of messages.

        Args:
            message_content (str): The content of the message to add
            room_code (str): The code of the chat room that the message was sent in
        """
        m = Message(
            message_content,
            self.username,
            room_code
        )
        self.messages.append(m)'''