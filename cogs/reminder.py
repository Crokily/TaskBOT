import discord
from discord.ext import tasks, commands
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import Task, Portfolio
from datetime import datetime, timedelta

class ReminderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reminded_tasks = set()  # To avoid duplicate reminders in one day
        self.last_date = datetime.now().date()
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    @tasks.loop(minutes=60)
    async def reminder_loop(self):
        db: Session = SessionLocal()
        now = datetime.now()

        # Reset reminders if the day has changed
        if now.date() != self.last_date:
            self.reminded_tasks.clear()
            self.last_date = now.date()

        # Calculate tomorrow's date
        tomorrow = now.date() + timedelta(days=1)
        # Query tasks that are due tomorrow
        tasks_due = db.query(Task).all()
        for task in tasks_due:
            if task.deadline.date() == tomorrow and task.task_id not in self.reminded_tasks:
                if now.hour == 9:  # Send reminders at 9:00 AM
                    portfolio = db.query(Portfolio).filter(Portfolio.portfolio_id == task.portfolio_id).first()
                    if portfolio:
                        try:
                            channel_id = int(portfolio.channel_id)
                            channel = self.bot.get_channel(channel_id)
                            if channel:
                                # Attempt to fetch the role in the guild with the name "DepartmentName-portfolio"
                                role_name = f"{portfolio.name} portfolio"
                                role = discord.utils.get(channel.guild.roles, name=role_name)
                                role_mention = role.mention if role else ""
                                embed = discord.Embed(
                                    title="⏰ Task Reminder",
                                    description=(
                                        f"Reminder: The task **{task.title}** (ID: {task.task_id}) is due tomorrow at "
                                        f"{task.deadline.strftime('%d/%m/%Y %H:%M')}."
                                    ),
                                    color=0xe67e22
                                )
                                embed.set_footer(text=f"Department: {portfolio.name}")
                                # Send the reminder message with role mention
                                await channel.send(content=role_mention, embed=embed)
                                self.reminded_tasks.add(task.task_id)
                        except Exception as e:
                            print(f"Error sending reminder: {e}")
        db.close()

    @reminder_loop.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(ReminderCog(bot))
