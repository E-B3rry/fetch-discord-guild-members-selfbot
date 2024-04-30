# Internal modules
import csv
import datetime
import re
import asyncio
import logging
from pathlib import Path
from typing import List, Optional

# Project modules
from constants import *

# External modules
import discord
from discord import Guild, TextChannel


class GuildMembersFetcher(discord.Client):
    """
    This class is the client for the Guild Members Fetcher bot
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the bot and the worker thread
        """
        super().__init__(**kwargs)

        # Logging system
        logging.basicConfig(
            level=logging.INFO, format="\x1b[0m%(asctime)s %(levelname)s %(message)s"
        )

        # Ensure OUTPUT_PATH exists
        Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

    async def on_ready(self) -> None:
        """
        Internally called method when the bot is ready
        :return: None
        """
        logging.info(f"Authenticated as {self.user} (ID: {self.user.id})\n")
        logging.info(f"Hello world!\n")

    async def on_message(self, message: discord.Message) -> None:
        """
        This method is internally called when a message is received
        :param message: The message received
        :return: None
        """
        # Ignore bot except from self
        if message.author.id != self.user.id:
            return

        # Check if the message is a command
        command = message.content.lower()
        if command.startswith("membersfetcher") or command.startswith("mf"):
            args = re.split(r"\s+", message.content.lower())
            await self.handle_commands(message, args)

    async def handle_commands(self, message: discord.Message, args: List[str]) -> None:
        """
        This method handle commands when the prefix or an alias is detected
        :return: None
        """
        await self.wait_until_ready()  # Wait for the bot to be ready

        logging.info(f"Received command: {args}")
        if len(args) > 1:
            match args[1]:
                case "help" | "h":
                    await message.reply(HELP_MESSAGE, mention_author=True)
                case "fetch" | "run":
                    if 3 <= len(args) <= 4:
                        # Fetch guild
                        try:
                            # Fetch guild name from guild id
                            guild_id = int(args[2])
                            guild = await self.fetch_guild(guild_id, with_counts=True)

                            if not guild:
                                raise ValueError(f"Guild {guild_id} not found")
                        except Exception as e:
                            await message.reply(f"Failed to fetch guild. See console for further information", mention_author=True)
                            logging.error(f"Failed to fetch guild: {e}")
                            return

                        await message.reply(f"Fetching members from guild \"{guild.name}\", this may take a while...", mention_author=True)

                        # Fetch members
                        try:
                            start = datetime.datetime.now()
                            count = await self.fetch_and_save_guild_members(guild, None if len(args) == 3 else args[3])
                            time_taken = round((datetime.datetime.now() - start).total_seconds(), 2)
    
                            logging.info(f"Time taken: {time_taken} seconds")
                            await message.reply(f"Successfully fetched {count} member.s from \"{guild.name}\" in {time_taken} seconds.", mention_author=True)
                        except Exception as e:
                            await message.reply(f"Failed to fetch members. See console for further information", mention_author=True)
                            logging.error(f"Failed to fetch members: {e}")
                    else:
                        await message.reply(BADLY_FORMATTED_COMMAND, mention_author=True)
                case "suicide" | "shutdown" | "kill":
                    # Kills instance
                    await message.reply(SUICIDE_MESSAGE, mention_author=True)
                    await self.close()
                case _:
                    await message.reply(BADLY_FORMATTED_COMMAND, mention_author=True)
        else:
            await message.reply(NOT_A_COMMAND, mention_author=True)

    async def fetch_and_save_guild_members(self, guild: Guild, filename: Optional[str] = None) -> int:
        """
        Fetches all the members from the guild and save it
        :param guild: The guild to scrap
        :param filename: The .csv file to save the scraped data, defaulting to {guild_name}-{now}.csv
        :return:
        """
        logging.info(f"Preparing the fetch of \"{guild.name}\" members...")
        # If no filename, generate one
        if filename is None:
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{self.sanitize_filename(guild.name)}-{now}.csv"  # Sanitize guild name just in case
        else:
            # If one is provided, sanitize it and ensure that it ends with .csv
            filename = self.sanitize_filename(filename)
            if not filename.endswith(".csv"):
                filename += ".csv"

        # Fetch all channels
        channels = await guild.fetch_channels()
        text_channels: list[TextChannel] = [channel for channel in channels if isinstance(channel, TextChannel)]
        logging.info(f"Found {len(text_channels)} text channels in guild \"{guild.name}\". Using them for scraping members.")

        # Fetch all members
        logging.info(f"Fetching members from guild \"{guild.name}\"...")
        members = await guild.fetch_members(channels=text_channels, cache=True, force_scraping=True, delay=MEMBER_SIDEBAR_SCRAPING_DELAY)
        members_count = len(members)
        logging.info(f"Found {members_count} members in guild \"{guild.name}\".")

        # Prepare data for csv
        data = [["ID", "Username", "Display name", "Joined server at", "Created account at", 
                 "Mutual guilds count", "Mutual friends count", 
                 "Mutual guilds", "Mutual friends"]]  # Header
        logging.info("Processing each member data...")
        for member in members:
            if member.id == self.user.id:
                continue  # Skip self

            # Fetch profile and process mutual friends and guilds string
            member_profile = await member.profile(with_mutual_guilds=True, with_mutual_friends=True, with_mutual_friends_count=True)
            mutual_friends_str = ", ".join([f"{friend.name} ({friend.id})" for friend in member_profile.mutual_friends])
            mutual_guilds_str = ", ".join([
                f"{self.get_guild(mutual_guild.id).name} ({mutual_guild.id})"
                for mutual_guild in member_profile.mutual_guilds
                if mutual_guild.id != guild.id  # Skip the current guild
            ])

            # Append line to data
            data.append([
                member.id, member.name, member.display_name, member.joined_at, member.created_at,
                len(member_profile.mutual_guilds) - 1, len(member_profile.mutual_friends),  # -1 to exclude the current guild
                mutual_guilds_str, mutual_friends_str
            ])
            
            # Show progress every 10 members processed
            current_members = len(data) - 1  # Exclude header
            if current_members % 10 == 0:
                logging.info(f"{round(current_members / members_count * 100, 1)}% members processed. ({len(data)}/{members_count})")

            # Delay to throttle
            await asyncio.sleep(MEMBER_SCRAPING_DELAY)
        logging.info("All members processed.")

        # Write data to csv (important: use utf8 to read it properly)
        file_path = Path(OUTPUT_PATH, filename)
        logging.info(f"Saving data (utf8) to \"{file_path}\"...")
        with open(file_path, 'w', newline='', encoding="utf8") as file:
            writer = csv.writer(file)
            writer.writerows(data)
        logging.info(f"Data saved to \"{file_path}\".")

        logging.info(f"Guild \"{guild.name}\" scraping done with {members_count} members!")
        return members_count

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitizes a filename
        :param filename: The filename to sanitize
        :return: The sanitized filename
        """
        return re.sub(r"\W+", '_', filename)

    async def close(self) -> None:
        """
        Closes the bot
        :return: None
        """
        logging.info(f"Goodbye world!\n")
        await super().close()
