# manage.py - A script used to manage the ChatApp database
from application.database import DataBase
from application.user import User


action = int(input("Type the number of the action you want to perform: 0 - Delete all messages from database; 1 - Create new user account: "))

if action == 0:
    db = DataBase()
    db.delete_all_messages()
    db.close()
    print("All messages cleared successfully.")
elif action == 1:
    username = input("Type the user's username: ")
    password = input("Type the user's password: ")
    u = User(username, password)
    db = DataBase()
    db.add_user(u)
    db.close()
    print(f"Success. User created with username `{username}`, password `{password}`, user type `{u.user_type}`, and user id `{u.user_id}`.")