import os
from pathlib import Path
from dotenv import load_dotenv


# Set the path to the .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Store Flask configurations from the .env file."""

    # Load environment variables
    SECRET_KEY = os.getenv("SECRET_KEY")
    SERVER = os.getenv("SERVER")
    DEBUG = os.getenv("DEBUG")