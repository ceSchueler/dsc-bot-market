import discord
from discord.ext import commands
import json
from datetime import datetime


class TransactionLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Define round end times
        self.rounds = {
            'R01': '2025-05-16T23:54:59.944Z',
            'R02': '2025-05-17T00:16:58.652Z',
            'R03': '2025-05-17T00:25:46.024Z',
            'R04': '2025-05-17T00:33:45.215Z',
            'R05': '2025-05-17T00:43:10.634Z',
            'R06': '2025-05-17T00:43:10.634Z',
            'R07': '2025-05-17T00:53:09.935Z',
            'R08': '2025-05-17T00:59:31.789Z',
            'R09': '2025-05-17T01:05:29.897Z',
            'R10': '2025-05-17T01:10:18.513Z',
            'R11': '2025-05-17T01:15:33.437Z',
            'R12': '2025-05-17T01:20:24.475Z',
            'R13': '2025-05-17T01:25:45.485Z',
            'R14': '2025-05-17T01:30:27.362Z',
            'R15': '2025-05-17T01:35:18.427Z',
            'R16': '2025-05-17T01:40:18.568Z',
            'R17': '2025-05-17T01:45:52.839Z'
        }

    def load_transactions(self):
        """Load transactions from JSON file."""
        try:
            with open("data/transactions.json", 'r') as f:
                data = json.load(f)
                return data.get("transactions", []) if isinstance(data, dict) else data
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get_round(self, timestamp: str) -> str:
        """Determine which round a transaction belongs to based on its timestamp."""
        trans_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        prev_round_end = None

        for round_name, round_end in self.rounds.items():
            round_end_time = datetime.fromisoformat(round_end.replace('Z', '+00:00'))
            if trans_time <= round_end_time:
                if prev_round_end is None or trans_time > prev_round_end:
                    return round_name
            prev_round_end = round_end_time
        return "After R17"

    @commands.command(name="transactionlog")
    async def transaction_log(self, ctx: commands.Context, user_id: int, transaction_type: str = None):
        """
        Get transaction log for a specific user.
        Usage: !transactionlog <user_id> [buy|sell]
        """
        transactions = self.load_transactions()
        if not transactions:
            await ctx.send("No transactions found.")
            return

        # Filter transactions for the specified user
        user_transactions = []
        for trans in transactions:
            if transaction_type:
                if transaction_type.lower() == 'buy' and trans['buyer_id'] == user_id:
                    user_transactions.append(trans)
                elif transaction_type.lower() == 'sell' and trans['seller_id'] == user_id:
                    user_transactions.append(trans)
            else:
                if trans['buyer_id'] == user_id or trans['seller_id'] == user_id:
                    user_transactions.append(trans)

        if not user_transactions:
            await ctx.send(f"No {'buy' if transaction_type else ''} transactions found for user <@{user_id}>.")
            return

        # Create the message
        messages = []
        current_message = f"Transaction log for <@{user_id}>"
        current_message += f" ({transaction_type.upper()})" if transaction_type else ""
        current_message += ":\n\n"

        # Sort transactions by timestamp
        user_transactions.sort(key=lambda x: x['timestamp'])

        current_round = None
        for trans in user_transactions:
            timestamp = datetime.fromisoformat(trans['timestamp'].replace('Z', '+00:00'))
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

            # Check if we need to add a new round header
            trans_round = self.get_round(trans['timestamp'])
            if trans_round != current_round:
                round_header = f"**{trans_round}**\n"
                if len(current_message + round_header) > 2000:
                    messages.append(current_message)
                    current_message = round_header
                else:
                    current_message += round_header
                current_round = trans_round

            transaction_line = (
                f"Transaction #{trans['transaction_id']:02} - {formatted_time}\n"
                f"Amount: ${trans['amount']}\n"
                f"{'Bought from' if trans['buyer_id'] == user_id else 'Sold to'} "
                f"<@{trans['seller_id'] if trans['buyer_id'] == user_id else trans['buyer_id']}>\n\n"
            )

            # Check if adding this line would exceed Discord's character limit
            if len(current_message + transaction_line) > 2000:
                messages.append(current_message)
                current_message = transaction_line
            else:
                current_message += transaction_line

        if current_message:
            messages.append(current_message)

        # Send all messages
        for message in messages:
            await ctx.send(message)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TransactionLog(bot))