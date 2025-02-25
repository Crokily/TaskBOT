import os
from dotenv import load_dotenv

# 加载.env文件中的变量
# load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
