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

    @commands.command(name="sethorsechannel")
    @commands.has_permissions(manage_channels=True)
    async def sethorsechannel(self, ctx: commands.Context) -> None:
        try:
            config = load_config()
            if "horsechannels" not in config:
                config["horsechannels"] = {}
            config["horsechannels"][str(ctx.channel.id)] = ctx.channel.name
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
    #@commands.has_permissions(administrator=True)
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
            await ctx.send("✅ This channel is now set as the log channel.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """
    Set up the HorseAdmin cog.
    
    Args:
        bot (commands.Bot): The bot instance to add this cog to
    """
    await bot.add_cog(HorseAdmin(bot))
