import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import Task, Portfolio
from datetime import datetime
from utils.date_util import parse_date

# Mapping status to emoji
STATUS_EMOJI = {
    "Not Started": "⏳",
    "In Progress": "▶️",
    "Completed": "✅",
    "Cancelled": "❌"
}

# Mapping status to button style
BUTTON_STYLE = {
    "Not Started": discord.ButtonStyle.secondary,    # Gray
    "In Progress": discord.ButtonStyle.primary,    # Blue
    "Completed": discord.ButtonStyle.success,        # Green
    "Cancelled": discord.ButtonStyle.danger          # Red
}

# Helper function: split long text into parts not exceeding max_length
def split_text(text: str, max_length: int = 1024):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Paginator view with jump buttons using emoji and count on labels.
class TaskPaginator(discord.ui.View):
    def __init__(self, pages: list, author: discord.User, status_jump: dict, status_counts: dict):
        super().__init__(timeout=180)
        self.pages = pages
        self.current = 0
        self.author = author
        self.status_jump = status_jump  # Mapping from status to the first page index for that status
        self.status_counts = status_counts  # Mapping from status to count

        # Row 0: Previous and Next buttons.
        prev_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary, row=0)
        next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary, row=0)
        prev_button.callback = self.previous_callback
        next_button.callback = self.next_callback
        self.add_item(prev_button)
        self.add_item(next_button)

        # Row 1: Jump buttons for each status.
        for status, first_page in self.status_jump.items():
            emoji = STATUS_EMOJI.get(status, "")
            count = self.status_counts.get(status, 0)
            label = f"{emoji}: {count}"
            btn = discord.ui.Button(label=label, style=BUTTON_STYLE.get(status, discord.ButtonStyle.secondary), row=1)
            # Capture first_page in the callback.
            async def jump_callback(interaction: discord.Interaction, page_index=first_page):
                if interaction.user != self.author:
                    await interaction.response.send_message("You cannot use these buttons.", ephemeral=True)
                    return
                self.current = page_index
                await self.update_message(interaction)
            btn.callback = jump_callback
            self.add_item(btn)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    async def previous_callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("You cannot use these buttons.", ephemeral=True)
            return
        if self.current > 0:
            self.current -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("Already at the first page.", ephemeral=True)

    async def next_callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("You cannot use these buttons.", ephemeral=True)
            return
        if self.current < len(self.pages) - 1:
            self.current += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("Already at the last page.", ephemeral=True)

class TaskCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create_task", description="Create a task for a specific portfolio")
    @app_commands.describe(
        portfolio_id="Select the portfolio where the task will be created",
        title="Title of the task",
        deadline="Deadline in format DD/MM/YYYY HH:MM or DD/MM/YYYY (time defaults to 00:00)",
        priority="Priority of the task",
        description="Task description (optional)"
    )
    @app_commands.choices(
        portfolio_id=[
            app_commands.Choice(name="IT", value=26),
            app_commands.Choice(name="MARKETING", value=27),
            app_commands.Choice(name="EVENTS", value=28)
        ],
        priority=[
            app_commands.Choice(name="Low", value="Low"),
            app_commands.Choice(name="Medium", value="Medium"),
            app_commands.Choice(name="High", value="High")
        ]
    )
    async def create_task(self, interaction: discord.Interaction, portfolio_id: int, title: str, deadline: str, priority: str = "Low", description: str = ""):
        # Parse the deadline
        deadline_dt = parse_date(deadline)
        if deadline_dt is None:
            await interaction.response.send_message("Error: Deadline format should be DD/MM/YYYY or DD/MM/YYYY HH:MM", ephemeral=True)
            return

        db: Session = SessionLocal()
        portfolio = db.query(Portfolio).filter(Portfolio.portfolio_id == portfolio_id).first()
        if not portfolio:
            await interaction.response.send_message("Error: Specified portfolio not found", ephemeral=True)
            db.close()
            return

        # Save necessary portfolio attributes before closing session
        department = portfolio.name
        portfolio_channel_id = portfolio.channel_id

        new_task = Task(
            title=title,
            description=description,
            deadline=deadline_dt,
            portfolio_id=portfolio_id,
            priority=priority,
            status="Not Started"
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        db.close()

        # Build the interaction response embed
        embed = discord.Embed(
            title=f"📝 New Task Created: {new_task.title}",
            description="Your task has been successfully created. Details are as follows:",
            color=0x00ff00
        )
        embed.add_field(name="Description", value=new_task.description or "None", inline=False)
        embed.add_field(name="Priority", value=f"🎯 {new_task.priority}", inline=True)
        embed.add_field(name="Status", value=f"{STATUS_EMOJI.get(new_task.status, '')} {new_task.status}", inline=True)
        embed.add_field(name="Deadline", value=new_task.deadline.strftime("%d/%m/%Y %H:%M") if new_task.deadline else "None", inline=True)
        embed.add_field(name="Department", value=department, inline=True)
        embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
        embed.set_footer(text=f"Task ID: {new_task.task_id}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Send channel notification in the corresponding portfolio channel and mention the role
        try:
            channel_id = int(portfolio_channel_id)
            channel = self.bot.get_channel(channel_id)
            if channel:
                role_name = f"{department} Portfolio"
                role = discord.utils.get(channel.guild.roles, name=role_name)
                role_mention = role.mention if role else ""
                notification_embed = discord.Embed(
                    title=f"📝 New Task Created: {new_task.title}",
                    description="A new task has been created with the following details:",
                    color=0x00ff00
                )
                notification_embed.add_field(name="Description", value=new_task.description or "None", inline=False)
                notification_embed.add_field(name="Priority", value=f"🎯 {new_task.priority}", inline=True)
                notification_embed.add_field(name="Status", value=f"{STATUS_EMOJI.get(new_task.status, '')} {new_task.status}", inline=True)
                notification_embed.add_field(name="Deadline", value=new_task.deadline.strftime("%d/%m/%Y %H:%M") if new_task.deadline else "None", inline=True)
                notification_embed.add_field(name="Department", value=department, inline=True)
                notification_embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
                notification_embed.set_footer(text=f"Task ID: {new_task.task_id}")
                await channel.send(content=role_mention, embed=notification_embed)
        except Exception as e:
            print(f"Error sending channel notification (create_task): {e}")

    @app_commands.command(name="edit_task", description="Update the status of a task")
    @app_commands.describe(
        task_id="ID of the task to edit",
        status="New status of the task"
    )
    @app_commands.choices(
        status=[
            app_commands.Choice(name="Not Started", value="Not Started"),
            app_commands.Choice(name="In Progress", value="In Progress"),
            app_commands.Choice(name="Completed", value="Completed"),
            app_commands.Choice(name="Cancelled", value="Cancelled")
        ]
    )
    async def edit_task(self, interaction: discord.Interaction, task_id: int, status: str):
        db: Session = SessionLocal()
        task_obj = db.query(Task).filter(Task.task_id == task_id).first()
        if not task_obj:
            await interaction.response.send_message("Error: Specified task not found", ephemeral=True)
            db.close()
            return

        old_status = task_obj.status
        task_obj.status = status
        db.commit()
        db.refresh(task_obj)
        # Save the portfolio_id before closing the session
        portfolio_id = task_obj.portfolio_id
        db.close()

        # Build the interaction response embed
        embed = discord.Embed(
            title=f"🔄 Task Updated: {task_obj.title}",
            description="The task status has been updated.",
            color=0x3498db
        )
        embed.add_field(name="Old Status", value=f"{STATUS_EMOJI.get(old_status, '')} {old_status}", inline=True)
        embed.add_field(name="New Status", value=f"{STATUS_EMOJI.get(task_obj.status, '')} {task_obj.status}", inline=True)
        embed.add_field(name="Task ID", value=task_obj.task_id, inline=True)
        embed.set_footer(text=f"Updated by: {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Send channel notification for task update
        try:
            db: Session = SessionLocal()
            portfolio = db.query(Portfolio).filter(Portfolio.portfolio_id == portfolio_id).first()
            if portfolio:
                # Save needed attributes before closing session
                department = portfolio.name
                portfolio_channel_id = portfolio.channel_id
            db.close()
            if portfolio:
                channel_id = int(portfolio_channel_id)
                channel = self.bot.get_channel(channel_id)
                if channel:
                    role_name = f"{department} Portfolio"
                    role = discord.utils.get(channel.guild.roles, name=role_name)
                    role_mention = role.mention if role else ""
                    notification_embed = discord.Embed(
                        title=f"🔄 Task Updated: {task_obj.title}",
                        description="The task status has been updated.",
                        color=0x3498db
                    )
                    notification_embed.add_field(name="Old Status", value=f"{STATUS_EMOJI.get(old_status, '')} {old_status}", inline=True)
                    notification_embed.add_field(name="New Status", value=f"{STATUS_EMOJI.get(task_obj.status, '')} {task_obj.status}", inline=True)
                    notification_embed.add_field(name="Task ID", value=task_obj.task_id, inline=True)
                    notification_embed.set_footer(text=f"Updated by: {interaction.user.display_name}")
                    await channel.send(content=role_mention, embed=notification_embed)
        except Exception as e:
            print(f"Error sending channel notification (edit_task): {e}")

    @app_commands.command(name="check_tasks", description="Display a list of tasks")
    @app_commands.describe(
        portfolio_id="Optional: Select a portfolio to filter tasks. If not provided, tasks from all departments will be displayed"
    )
    @app_commands.choices(
        portfolio_id=[
            app_commands.Choice(name="IT", value=26),
            app_commands.Choice(name="MARKETING", value=27),
            app_commands.Choice(name="EVENTS", value=28)
        ]
    )
    async def check_tasks(self, interaction: discord.Interaction, portfolio_id: int = None):
        db: Session = SessionLocal()
        if portfolio_id:
            tasks_list = db.query(Task).filter(Task.portfolio_id == portfolio_id).all()
            department = db.query(Portfolio).filter(Portfolio.portfolio_id == portfolio_id).first().name
        else:
            tasks_list = db.query(Task).all()
            portfolios = db.query(Portfolio).all()
            portfolio_map = {p.portfolio_id: p.name for p in portfolios}
        db.close()

        if not tasks_list:
            await interaction.response.send_message("No tasks found.", ephemeral=True)
            return

        # Group tasks by status and count them.
        grouped_tasks = {}
        status_counts = {}
        for task in tasks_list:
            status = task.status
            grouped_tasks.setdefault(status, []).append(task)
            status_counts[status] = status_counts.get(status, 0) + 1

        # Fixed status order.
        statuses_order = ["Not Started", "In Progress", "Completed", "Cancelled"]

        pages = []
        status_jump = {}  # Mapping from status to first page index.
        current_page_index = 0

        for status in statuses_order:
            if status not in grouped_tasks:
                continue
            entries = []
            for task in grouped_tasks[status]:
                deadline_str = task.deadline.strftime("%d/%m/%Y %H:%M") if task.deadline else "None"
                entry = (f"**ID:** {task.task_id} | **Title:** {task.title}\n"
                         f"**Description:** {task.description or 'None'}\n"
                         f"**Priority:** {task.priority}\n"
                         f"**Deadline:** {deadline_str}")
                if not portfolio_id:
                    dept = portfolio_map.get(task.portfolio_id, "Unknown")
                    entry += f"\n**Department:** {dept}"
                entries.append(entry)
            group_text = "\n\n".join(entries)
            chunks = split_text(group_text, 1024)
            for idx, chunk in enumerate(chunks):
                embed = discord.Embed(title="📋 Task List", color=0x9b59b6)
                if portfolio_id:
                    embed.description = f"Tasks for **{department}** department."
                else:
                    embed.description = "Tasks for **all departments**."
                embed.add_field(name=f"{STATUS_EMOJI.get(status, '')} {status} (Page {idx+1}/{len(chunks)})", value=chunk, inline=False)
                # embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                pages.append(embed)
                if idx == 0:
                    status_jump[status] = current_page_index
                current_page_index += 1

        if not pages:
            await interaction.response.send_message("No tasks found.", ephemeral=True)
            return

        if len(pages) == 1:
            await interaction.response.send_message(embed=pages[0], ephemeral=True)
        else:
            paginator = TaskPaginator(pages, interaction.user, status_jump, status_counts)
            await interaction.response.send_message(embed=pages[0], view=paginator, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TaskCog(bot))