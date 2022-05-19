import datetime
import pytz
import time
import random
from dateutil import tz


class Message:

    def __init__(self, content: str, author_id: int, author_username: str, room_code: str="GLOBAL", replying_to: int=0):
        """Initalizese a new message object containing the message content, author username, timestamp
        formatted as a datetime, the pretty timestamp (a more readable string), and the message id

        Args:
            content (str): The message content
            author_id (int): The ID of the user who sent the message
            author_username (str): The username of the user who sent the message
            room_code (str): The room code in which the message wast sent in. Defaults to "GLOBAL"
            replying_to (int): The ID of the message that this message is replying to. Defaults to 0
        """
        self.content = content
        self.author_id = author_id
        self.author_username = author_username
        self.timestamp = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone("US/Eastern")) # Conver the UTC timestamp into an EST timestamp using pytz
        self.pretty_timestamp = self.timestamp.strftime("%I:%M %p on %A, %B %d %Y")
        self.msg_id = int(str(round(time.time())) + str(random.randint(1000, 9999))) # Construct a random message id using the current time and a random number
        self.room_code = room_code
        self.replying_to = replying_to

    def to_dict(self):
        return {
            "content": self.content,
            "author_id": self.author_id,
            "author_username": self.author_username,
            "timestamp": self.pretty_timestamp,
            "msg_id": self.msg_id,
            "room_code": self.room_code,
            "replying_to": self.replying_to
        }

    @classmethod
    def construct_message(cls, content: str, author_id: int, author_username: str, timestamp: datetime, room_code: str, msg_id: int, replying_to: int):
        """Constructs a message object using pre-existing message data provided
        as the arguments.

        Args:
            content (str): The content of the message
            author_id (int): The user_id of the user who sent the message
            author_username (str): The username of the author of the message
            timestamp (datetime): The datetime timestamp of the message
            room_code (str): The code of the room which the message was sent in
            msg_id (int): The unique id of the message
            replying_to (int): The ID of the message that this message is replying to

        Returns:
            Message: A new message object
        """
        if type(timestamp) == str:
            timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
        # Convert timestamp from UTC datetime to EST
        elif type(timestamp) == datetime.datetime:
            timestamp = timestamp.replace(tzinfo=tz.tzutc())
            timestamp = timestamp.astimezone(tz.gettz("US/Eastern"))
        m = Message(content, author_id, author_username, room_code)
        m.timestamp = timestamp
        m.pretty_timestamp = m.timestamp.strftime("%I:%M %p on %A, %B %d %Y")
        m.msg_id = int(msg_id)
        m.replying_to = replying_to
        return m