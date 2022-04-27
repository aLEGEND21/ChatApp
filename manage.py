# manage.py - A script used to manage the ChatApp database
from application.database import DataBase
from application.user import User


action = int(input("Type the number of the action you want to perform: 0 - Delete all messages from database; 1 - Create new user account; 2 - Create a user account using claim codes: "))

if action == 0:
    db = DataBase()
    db.delete_all_messages()
    db.close()
    print("All messages cleared successfully.")
elif action == 1:
    username = input("Type the user's username: ")
    password = input("Type the user's password: ")
    user_type = int(input("Type the user type, 1 for superuser and 0 for regular user: "))
    u = User(username, password, user_type)
    db = DataBase()
    db.add_user(u)
    db.close()
    print(f"Success. User created with username `{username}`, password `{password}`, user type `{u.user_type}`, and user id `{u.user_id}`.")
# This doesn't work because the claim_codes var cannot be accessed when the script is running
elif action == 2:
    raise Exception("This is non-operational.")
    claim_code = input("Type the claim code: ")
    username = input("Type the user's username: ")
    claim_codes.append({"claim_code": claim_code, "username": username})
    print("Successfully created claim code:", claim_code)