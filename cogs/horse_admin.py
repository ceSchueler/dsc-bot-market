from typing import Dict

from discord.ext import commands

from utils.config_utils import load_config, save_config

class HorseAdmin(commands.Cog):
    """
    A cog for managing horse trading channels and related functionality.
    
    This cog provides commands for setting up horse trading channels,
    managing their state, and configuring logging channels.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the HorseAdmin cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is attached to
        """
        self.bot = bot

    @commands.command(name="sethorsechannel")
    @commands.has_permissions(manage_channels=True)
    async def sethorsechannel(self, ctx: commands.Context) -> None:
        try:
            config = load_config()
            if "horsechannels" not in config:
                config["horsechannels"] = {}
            config["horsechannels"][ctx.channel.id] = ctx.channel.name
            save_config(config)
            
            # Reload configuration in Trading cog
            trading_cog = self.bot.get_cog('Trading')
            if trading_cog:
                trading_cog.reload_config()
            
            await ctx.send(f"✅ This channel is now configured for horse trading.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.command(name="close")
    @commands.has_permissions(manage_channels=True)
    async def closehorse(self, ctx: commands.Context) -> None:
        """
        Close the current channel for horse trading.
        
        Args:
            ctx (commands.Context): The command context
        """
        try:
            config = load_config()
            config["closed_channels"] = config.get("closed_channels", [])
            config["horsechannels"] = config.get("horsechannels", {})
            cid = ctx.channel.id
            if str(cid) not in config["horsechannels"]:
                await ctx.send("This channel is not set up for horse trading. Use `!sethorsechannel` first.",
                               ephemeral=True)
                return

            if cid not in config["closed_channels"]:
                config["closed_channels"].append(cid)
                save_config(config)
                await ctx.send("🚫 Trading in this channel is now closed.")
            else:
                await ctx.send("Channel is already closed.", ephemeral=True)

            # Reload configuration in Trading cog
            trading_cog = self.bot.get_cog('Trading')
            if trading_cog:
                trading_cog.reload_config()
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.command(name="open")
    @commands.has_permissions(manage_channels=True)
    async def openhorse(self, ctx: commands.Context) -> None:
        """
        Open the current channel for horse trading.

        Args:
            ctx (commands.Context): The command context
        """
        try:
            config = load_config()
            config["closed_channels"] = config.get("closed_channels", [])
            config["horsechannels"] = config.get("horsechannels", {})
            cid = ctx.channel.id
            if str(cid) not in config["horsechannels"]:
                await ctx.send("This channel is not set up for horse trading. Use `!sethorsechannel` first.",
                               ephemeral=True)
                return

            if cid in config["closed_channels"]:
                config["closed_channels"].remove(cid)  # Changed this line
                save_config(config)
                await ctx.send("✅ Channel is now open for horse trading.")
            else:
                await ctx.send("Channel is not closed. Did you set it as horsechannel with `!sethorsechannel`?", ephemeral=True)

            # Reload configuration in Trading cog
            trading_cog = self.bot.get_cog('Trading')
            if trading_cog:
                trading_cog.reload_config()
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.command(name="setlogchannel")
    @commands.has_permissions(manage_channels=True)
    async def setlogchannel(self, ctx: commands.Context) -> None:
        """
        Set the current channel as the central transaction log.

        Args:
            ctx (commands.Context): The command context
        """
        try:
            config = load_config()
            # Store the channel ID as an integer to maintain consistency
            config["log_channel"] = ctx.channel.id
            save_config(config)

            # Reload configuration in Trading cog to ensure it's updated
            trading_cog = self.bot.get_cog('Trading')
            if trading_cog:
                trading_cog.reload_config()

            await ctx.send("✅ This channel is now set as the log channel.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.command(name="reset")
    @commands.has_permissions(manage_channels=True)
    async def reset(self, ctx: commands.Context) -> None:
        """
        Reset all configuration and transaction data to empty state.
        Requires administrator permissions.

        Args:
            ctx (commands.Context): The command context
        """
        try:
            # Reset config.json to empty object
            with open('data/config.json', 'w') as config_file:
                config_file.write('{}')

            # Reset transactions.json to empty array
            with open('data/transactions.json', 'w') as transactions_file:
                transactions_file.write('[]')

            # Reload configuration in Trading cog
            trading_cog = self.bot.get_cog('Trading')
            if trading_cog:
                trading_cog.reload_config()

            await ctx.send("✅ Successfully reset all data files.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)


    @commands.command(name="softreset")
    @commands.has_permissions(manage_channels=True)
    async def softreset(self, ctx: commands.Context) -> None:
        """
        Perform a soft reset that clears transactions and removes closed channels,
        while preserving other configuration data.

        Args:
            ctx (commands.Context): The command context
        """
        try:
            # Reset transactions.json to empty array
            with open('data/transactions.json', 'w') as transactions_file:
                transactions_file.write('[]')

            # Load and modify config to remove closed channels
            config = load_config()
            config["closed_channels"] = []  # Reset closed channels list
            config["trade_counter"] = 0  # Reset trade counter
            save_config(config)

            # Reload configuration in Trading cog
            trading_cog = self.bot.get_cog('Trading')
            if trading_cog:
                trading_cog.reload_config()

            await ctx.send("✅ Successfully reset transactions and cleared closed channels.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """
    Set up the HorseAdmin cog.
    
    Args:
        bot (commands.Bot): The bot instance to add this cog to
    """
    await bot.add_cog(HorseAdmin(bot))