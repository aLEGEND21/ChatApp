import datetime
import time
import random


class Message:

    def __init__(self, content: str, author_username: str):
        """Initalizese a new message object containing the message content, author username, timestamp
        formatted as a datetime, the pretty timestamp (a more readable string), and the message id

        Args:
            content (str): The message content
            author_username (str): The username of the user who sent the message
        """
        self.content = content
        self.author_username = author_username
        self.timestamp = datetime.datetime.now()
        self.pretty_timestamp = self.timestamp.strftime("%I:%M %p on %A, %B %d %Y")
        self.msg_id = int(str(round(time.time())) + str(random.randint(1000, 9999))) # Construct a random message id using the current time and a random number
    
    def to_dict(self):
        return {
            "content": self.content,
            "author_username": self.author_username,
            "timestamp": self.pretty_timestamp
        }

    @classmethod
    def construct_message(cls, content: str, author_username: str, timestamp: datetime, msg_id: int):
        """Constructs a message object using pre-existing message data provided
        as the arguments.

        Args:
            content (str): The content of the message
            author_username (str): The username of the user who sent the message
            timestamp (datetime): The datetime timestamp of the message
            msg_id (int): The unique id of the message

        Returns:
            Message: A new message object
        """
        if type(timestamp == str):
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        m = Message(content, author_username)
        m.timestamp = timestamp
        m.pretty_timestamp = m.timestamp.strftime("%I:%M %p on %A, %B %d %Y")
        m.msg_id = msg_id
        return m