import os
from pathlib import Path
from dotenv import load_dotenv


# Set the path to the .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Store Flask configurations from the .env file."""

    # Load environment variables
    DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
    DEBUG = os.getenv("DEBUG")
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SITE_URL = os.getenv("SITE_URL")