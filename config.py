import os
from dotenv import load_dotenv

# Load variables from .env file
# load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
