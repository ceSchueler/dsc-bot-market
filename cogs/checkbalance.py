from typing import Dict
import json
from discord.ext import commands
from utils.config_utils import load_config, save_config


class CheckBalance(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def check_channel(ctx: commands.Context) -> bool:
        """Check if command is used in allowed channels."""
        return not ('horse' in ctx.channel.name.lower() or 'log' in ctx.channel.name.lower())

    @commands.command(name="balance")
    @commands.check(check_channel)
    async def checkbalance(self, ctx: commands.Context, member: commands.MemberConverter = None) -> None:
        """Check balance and total transactions for yourself or another user.

        Args:
            ctx: The command context
            member: Optional member to check balance for. If not provided, checks own balance.
        """
        target_user = member if member else ctx.author
        user_id = target_user.id
        balance = 0
        stock = []  # Initialize as empty list
        # Load transactions to count total trades
        transactions = self.load_transactions()
        user_transactions = [
            t for t in transactions["transactions"]  # Removed .get() here
            if t["buyer_id"] == user_id or t["seller_id"] == user_id
        ]
        horse_hype_counts = {}
        messages = []

        for ut in user_transactions:
            channel = self.bot.get_channel(ut["channel_id"])
            channel_name = channel.name if channel else f"Channel {ut['channel_id']}"
            if ut["buyer_id"] == user_id:
                balance -= ut["amount"]
                stock.append(f"ID: {ut['transaction_id']} - {channel_name} bought for {ut['amount']}")
                if channel and "horse" in channel.name.lower():
                    clean_name = channel.name.replace("horse-of-", "")
                    if clean_name not in horse_hype_counts:
                        horse_hype_counts[clean_name] = 0
                    horse_hype_counts[clean_name] += 1
            elif ut["seller_id"] == user_id:
                balance += ut["amount"]
                stock.append(f"ID: {ut['transaction_id']} - {channel_name} sold for {ut['amount']}")
                if channel and "horse" in channel.name.lower():
                    clean_name = channel.name.replace("horse-of-", "")
                    if clean_name not in horse_hype_counts:
                        horse_hype_counts[clean_name] = 0
                    horse_hype_counts[clean_name] -= 1

        # Create the balance message
        messages = []
        current_message = f"# Balance Report for {target_user.name}\n"
        current_message += f"Current Balance: ➕/➖ ${balance}\n"
        current_message += f"Total Transactions: {len(user_transactions)}\n"

        # Add transactions with splitting if needed
        if stock:
            current_message += "Transaction History:\n"
            for transaction in stock:
                line = f"- {transaction}\n"
                # Check if adding this line would exceed the limit
                if len(current_message + line) > 1900:
                    messages.append(current_message)
                    current_message = "Transaction History (continued):\n"
                current_message += line

        # Add horse hype section
        horse_hype_section = f"\n# HORSE HYPE\n"
        horse_hype_section += f"-# Since I'm live coding this and adding this in on the fly the numbers below may be inaccurate\n"
        if horse_hype_counts:
            for horse, count in horse_hype_counts.items():
                horse_hype_section += f"- {horse}: {count} hype\n"
        else:
            horse_hype_section += "- No horse hype owned\n"

        # Check if adding horse hype section would exceed limit
        if len(current_message + horse_hype_section) > 1900:
            messages.append(current_message)
            current_message = horse_hype_section
        else:
            current_message += horse_hype_section

        # Add the final message if it's not empty
        if current_message:
            messages.append(current_message)

        # Send all messages
        for msg in messages:
            await ctx.send(msg)

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