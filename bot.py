import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.config_utils import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingBot(commands.Bot):
    """
    Custom bot class with additional functionality for trading system.
    """

    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description="A Discord bot for managing horse trading channels"
        )

        # Initialize bot state
        self.transaction_counter = 1
        self.ready = False

        # Load config
        config = load_config()
        self.logchannel = config.get("log_channel")
        self.horse_channels = config.get("horsechannels", {})

    async def setup_hook(self):
        """
        This is called when the bot is started up
        """
        # Load all cogs
        await self.load_extensions()
        logger.info("Bot is ready to start!")

    async def load_extensions(self):
        """
        Loads all cog extensions from the cogs directory
        """
        cogs_dir = Path(__file__).parent / "cogs"
        for filename in cogs_dir.glob("*.py"):
            if filename.stem == "__init__":
                continue

            try:
                await self.load_extension(f"cogs.{filename.stem}")
                logger.info(f"Loaded extension: {filename.stem}")
            except Exception as e:
                logger.error(f"Failed to load extension {filename.stem}: {e}")

    async def on_ready(self):
        """
        Called when the bot is ready and connected to Discord
        """
        if self.ready:
            await self.notify_channels("Bot is Online again!")
            return

        self.ready = True
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        await self.notify_channels("Bot is Online (again)!")

        # Set bot presence
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="horse trading channels"
            )
        )

    async def notify_channels(self, message: str):
        """Send a message to all horse channels and log channel."""
        for channel_id in self.horse_channels:
            try:
                channel = self.get_channel(channel_id)
                if channel:
                    await channel.send(message)
            except Exception as e:
                print(f"Failed to send message to channel {channel_id}: {e}")

        # Send to log channel
        if self.logchannel:
            try:
                log_channel = self.get_channel(self.logchannel)
                if log_channel:
                    await log_channel.send(message)
            except Exception as e:
                print(f"Failed to send message to log channel: {e}")


def main():
    """
    Main entry point for the bot
    """
    # Load environment variables
    load_dotenv()

    # Get the token from environment variables
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("No token found in .env file")

    # Create and run bot
    bot = TradingBot()

    try:
        bot.run(token, log_handler=None)
    except discord.errors.LoginFailure:
        logger.error("Failed to log in: Invalid token")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
