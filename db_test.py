from application.database import DataBase
from application.message import Message

db = DataBase()
m = Message("Another msg sent at 3:15 PM", "Joe")
db.add_message(m)

ms = db.get_all_messages()
for m in ms:
    print(m.content, m.author_username, m.pretty_timestamp) # WORKING :)