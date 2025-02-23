import discord
from discord.ext import commands
import os
from config import DISCORD_TOKEN

class MyBot(commands.Bot):
    async def setup_hook(self):
        # 加载 cogs 目录下的所有扩展
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                await self.load_extension(f"cogs.{filename[:-3]}")
        # 同步 Slash Commands 到 Discord（首次部署时可能需要一些时间更新）
        await self.tree.sync()

intents = discord.Intents.default()
intents.message_content = True

bot = MyBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'已登录为 {bot.user} (ID: {bot.user.id})')

bot.run(DISCORD_TOKEN)
