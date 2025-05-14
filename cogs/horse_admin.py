from typing import Dict

from discord.ext import commands

from utils.config_utils import load_config, save_config

# Define constants at module level
HORSE_EMOJIS: Dict[str, str] = {
    "A": "🇦",
    "B": "🇧",
    "C": "🇨",
    "D": "🇩",
    "E": "🇪",
    "F": "🇫",
    "G": "🇬"
}


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

    @commands.command(name="sethorse")
    @commands.has_permissions(manage_channels=True)
    async def sethorse(self, ctx: commands.Context, letter: str) -> None:
        """
        Set the current channel as a horse trading channel.
        
        Args:
            ctx (commands.Context): The command context
            letter (str): The horse letter to assign to this channel
        """
        letter = letter.upper()
        if letter not in HORSE_EMOJIS:
            await ctx.send(
                f"Invalid horse letter. Please use one of: {', '.join(HORSE_EMOJIS.keys())}",
                ephemeral=True
            )
            return

        try:
            config = load_config()
            config["horses"] = config.get("horses", {})
            config["horses"][str(ctx.channel.id)] = letter
            save_config(config)
            await ctx.send(f"✅ This channel is now for Horse {letter} {HORSE_EMOJIS[letter]} trading.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.command(name="closehorse")
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
            cid = str(ctx.channel.id)

            if cid not in config["closed_channels"]:
                config["closed_channels"].append(cid)
                save_config(config)
                await ctx.send("🚫 Trading in this channel is now closed.")
            else:
                await ctx.send("Channel is already closed.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.command(name="setlogchannel")
    @commands.has_permissions(administrator=True)
    async def setlogchannel(self, ctx: commands.Context) -> None:
        """
        Set the current channel as the central transaction log.
        
        Args:
            ctx (commands.Context): The command context
        """
        try:
            config = load_config()
            config["log_channel"] = str(ctx.channel.id)
            save_config(config)
            await ctx.send("✅ This channel is now set as the transaction log.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """
    Set up the HorseAdmin cog.
    
    Args:
        bot (commands.Bot): The bot instance to add this cog to
    """
    await bot.add_cog(HorseAdmin(bot))
