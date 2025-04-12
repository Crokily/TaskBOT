import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# 默认时区设置，如果.env中没有指定，则使用'Australia/Sydney'
TIMEZONE = os.getenv("TIMEZONE", "Australia/Sydney")
