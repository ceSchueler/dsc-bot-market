from typing import Dict
import json
from discord.ext import commands
from utils.config_utils import load_config, save_config


class CheckBalance(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="balance")
    async def checkbalance(self, ctx: commands.Context) -> None:
        """Check your balance and total transactions."""
        user_id = ctx.author.id
        balance = 0
        stock = []  # Initialize as empty list
        # Load transactions to count total trades
        transactions = self.load_transactions()
        user_transactions = [
            t for t in transactions["transactions"]  # Removed .get() here
            if t["buyer_id"] == user_id or t["seller_id"] == user_id
        ]
        for ut in user_transactions:
            channel = self.bot.get_channel(ut["channel_id"])
            channel_name = channel.name if channel else f"Channel {ut['channel_id']}"
            if ut["buyer_id"] == user_id:
                balance += ut["amount"]
                stock.append(f"ID: {ut['transaction_id']} - {channel_name} bought for {ut['amount']}")
            elif ut["seller_id"] == user_id:
                balance -= ut["amount"]
                stock.append(f"ID: {ut['transaction_id']} - {channel_name} sold for {ut['amount']}")

        # Create the balance message
        message = f"# Balance Report for {ctx.author.name}\n"
        message += f"Current Balance: ${balance}\n"
        message += f"Total Transactions: {len(user_transactions)}\n"
        if stock:
            message += "Transaction History:\n"
            for s in stock:
                message += f"- {s}\n"

        await ctx.send(message)

    def load_transactions(self) -> Dict:
        """Load transactions from JSON file."""
        try:
            with open("data/transactions.json", 'r') as f:
                data = json.load(f)
                # Ensure we have a transactions key with a list
                if isinstance(data, list):
                    return {"transactions": data}
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return {"transactions": []}


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CheckBalance(bot))