# Discord Task Manager Bot with Reminders

A simple Discord bot that provides basic task management functionality along with scheduled reminders. The bot allows users to create, update, and check tasks using slash commands and sends reminder notifications to corresponding channels with role mentions.

## Collaboration Guide
Check out the [Collaboration Guide](docs/COLLABORATION_GUIDE.md) for details on contributing to the project.

## Features

- **Task Management:**  
  - Create tasks with title, description, deadline, priority, and department (portfolio).  
  - Update task status using slash commands.  
  - Check tasks with beautiful embed messages, grouping tasks by status with pagination and direct jump buttons.

- **Scheduled Reminders:**  
  - The bot automatically checks tasks and sends a reminder notification on the corresponding channel one day before a task's deadline at 9:00 AM.
  - Reminders include a role mention for the department (e.g., `@IT Portfolio`).

- **Technologies Used:**  
  - [discord.py v2](https://discordpy.readthedocs.io/en/stable/) (Slash Commands and UI Views)  
  - [SQLAlchemy](https://www.sqlalchemy.org/) for ORM database interactions  
  - [python-dotenv](https://pypi.org/project/python-dotenv/) for environment variable management  
  - PostgreSQL (Supabase) as the database backend

## Directory Structure

```
discord_bot_task_management/
├── .env
├── README.md
├── requirements.txt
├── main.py
├── config.py
├── database/
│   ├── __init__.py
│   ├── db.py
│   └── models.py
├── cogs/
│   ├── __init__.py
│   ├── tasks.py
│   └── reminder.py
└── utils/
    ├── __init__.py
    ├── date_util.py
    └── formatter.py
```

- **.env**: Stores your environment variables such as `DATABASE_URL` and `DISCORD_TOKEN`.
- **main.py**: The entry point for the bot. It initializes the bot, loads all cogs, and starts the bot.
- **config.py**: Loads environment variables using python-dotenv.
- **database/**: Contains the SQLAlchemy database connection (db.py) and models (models.py) for tasks and portfolios.
- **cogs/**: Contains the command implementations:
  - `tasks.py`: Handles task management commands (create, edit, check tasks).
  - `reminder.py`: Implements scheduled reminders using discord.ext.tasks.
- **utils/**: Contains helper functions such as date parsing and message formatting.

## Setup & Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/discord_bot_task_management.git
   cd discord_bot_task_management
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   Create a `.env` file in the root directory with the following content:

   ```dotenv
   DATABASE_URL=postgresql://username:password@host:port/dbname
   DISCORD_TOKEN=your_discord_bot_token
   ```

5. **Set up your database:**

   Ensure your Supabase (PostgreSQL) database is running and that the `portfolios` and `tasks` tables are created as described.

6. **Run the bot:**

   ```bash
   python main.py
   ```

## Usage

- **Slash Commands:**  
  Use the slash commands provided by the bot (e.g., `/create_task`, `/edit_task`, `/check_tasks`) to manage tasks.

- **Task Notifications:**  
  Upon creating or updating tasks, the bot will send a notification in the corresponding portfolio channel and mention the department role (e.g., `@IT Portfolio`).

- **Task Check Pagination:**  
  When checking tasks, if the result spans multiple pages, navigation buttons (Previous, Next, and jump buttons with emoji and counts) are provided for easy browsing.

## Contributing

Contributions are welcome! Feel free to open issues or pull requests for improvements and bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).
