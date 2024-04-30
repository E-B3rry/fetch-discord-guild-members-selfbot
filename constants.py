from pathlib import Path

TOKEN = ""  # token-no-commit

OUTPUT_PATH = Path("out")

MEMBER_SIDEBAR_SCRAPING_DELAY = 0.1
MEMBER_SCRAPING_DELAY = 0.5


HELP_MESSAGE = """
**Members Fetcher Help**
- *Alias: 'mf'*
**membersfetcher help | h** - Display this message
**membersfetcher fetch | run <guild_id> [<file_name>]** - Fetch members from guild and save them into a .csv file
**membersfetcher shutdown | suicide | kill** - Kills the bot instance
"""

SUICIDE_MESSAGE = "Bot is shutting down. Goodbye world!"

BADLY_FORMATTED_COMMAND = "The command is not formatted properly, please refer to `mf help` for commands usage."
NOT_A_COMMAND = "Please use `mf help` to see available commands."
