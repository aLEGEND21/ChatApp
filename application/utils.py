import functools
import json
import re
from markupsafe import Markup
from markdown import markdown
from profanity import censor_profanity
from flask import redirect
from flask import url_for
from flask import session


# DECORATORS

def logged_in(func):
    """Checks whether the user is logged in to the application by checking if there is a valid
    user key in the session dict. If there is not, then the user is redirected to the login
    page of the application.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("user") is None:
            return redirect(url_for("views.login"))
        else:
            return func(*args, **kwargs)
    return wrapper

def is_superuser(func):
    """Checks whether the user is a superuser before allowing them to access the url route. If 
    they are not a superuser, they are redirected back to the home page.
    """
    @functools.wraps(func)
    @logged_in
    def wrapper(*args, **kwargs):
        if session.get("user").user_type != 1:
            return redirect(url_for("views.home"))
        else:
            return func(*args, **kwargs)
    return wrapper


# FUNCTIONS

def get_all_emojis():
    """Gets all emojis from the JSON file containing the emojis and returns them. The emojis are
    formatted as {emoji_name: emoji}.

    Returns:
        dict: A dict of all emojis with the emoji name as the key and the emoji as the value.
    """
    # Note: Similar emojis have been removed from the json file such as emojis with different skin tones
    # Note: The emoji file was sourced from: https://github.com/ArkinSolomon/discord-emoji-converter/blob/master/emojis.json
    with open("./emojis.json", 'rb') as f:
        emojis = json.load(f)
    return emojis

def markup_str(content: str, markup_chars: str, query_chars: str, replace_with: list):
    """Marks up parts of a string with html if they are surrounded by the markup char. This is useful
    to allow users to add variance to their messages while making sure that only safe characters are being
    used when they are adding variance to their messages.

    Args:
        content (str): The content of the message to be processed
        markup_chars (str): The escaped characters to supply to the regex
        query_chars (str): The exact characters to look for when replacing chars in the string
        replace_with (list): The html to replace the characters with. The opening tag and closing tag
            should be seperate elements in the list.

    Returns:
        str: The marked up message content
    """
    regex = re.compile(f'{markup_chars}(.*?){markup_chars}')
    for result in regex.findall(content):
        replace_str = query_chars + result + query_chars
        new_str = replace_with[0] + result + replace_with[1]
        content = content.replace(replace_str, new_str)
    return content

def parse_message(content):
    """Parse the message contents and remove profanity, replace emoji codes with the actual
    emojis, and escape any html for non-superuser accounts. 

    Args:
        content (str): The contents of the message to parse

    Returns:
        str: The parsed and edited message contents
    """
    # Replace all emoji names with the actual emoji in the message content. This is done by slicing 
    # the message content on the colon character and then trying to get each message fragment from
    # the dict containing all the emojis. This is fast because of Big O time complexity
    emoji_data = get_all_emojis()
    m_content = content.split(":")
    for emoji_name in m_content:
        emoji = emoji_data.get(emoji_name.lower())
        if emoji is not None:
            content = content.replace(f":{emoji_name}:", emoji)
    
    # Escape any html in the message if the user is not a superuser. Otherwise, convert the markdown into html
    if session.get("user").user_type != 1:
        content = str(Markup.escape(content))
    else:
        content = str(markdown(content)) # NOTE: This is experimental since markdown content in messages doesn't render correctly with deletes/edits
    
    # Markup up the message content based on what markup characters the user used in their message
    content = markup_str(content, r'\*\*', "**", ["<b>", "</b>"]) # Bolded
    content = markup_str(content, r'\*', "*", ["<i>", "</i>"]) # Italicized
    content = markup_str(content, r'\_\_', "__", ["<u>", "</u>"]) # Underlined
    
    # Detect urls and make them clickable
    urlRegex = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
    for result in urlRegex.findall(content):
        content = content.replace(result[0], f'<a href="{result[0]}" target="_blank">{result[0]}</a>')
    
    # Filter out any profanity from the message content
    content = censor_profanity(content)
    
    return content



# VARIABLES

claim_codes = [] # Contains all active claim codes in the application
public_rooms = ["Suggestions", "Feedback"] # Contains the room codes for all the public rooms in the application
ratelimits = {} # Contains the user ID and when the last message was sent