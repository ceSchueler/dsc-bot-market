import re
from typing import Optional, Tuple

import discord
from discord.ext import commands

from utils.config_utils import load_config, save_config
from utils.emoji_utils import EmojiManager
from utils.trading_utils import TradingManager, Offer


class Trading(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.trading_manager = TradingManager()
        self.emoji_manager = EmojiManager()
        self.offers = {}  # channel_id: list of offers

        # Load configuration
        config = load_config()
        self.finished_horses = set(config.get("closed_channels", []))
        self.transaction_counter = config.get("trade_counter", 1)
        self.logchannel = config.get("log_channel")
        self.horse_channels = config.get("horsechannels", {})

    def reload_config(self):
        config = load_config()
        self.finished_horses = set(config.get("closed_channels", []))
        self.transaction_counter = config.get("trade_counter", 1)
        self.logchannel = config.get("log_channel")
        self.horse_channels = config.get("horsechannels", {})

    def load_offers(self) -> None:
        """Load offers from the JSON file."""
        if os.path.exists(OFFERS_FILE):
            try:
                with open(OFFERS_FILE, 'r') as f:
                    saved_offers = json.load(f)

                # Convert saved data back to Offer objects
                for channel_id, offers in saved_offers.items():
                    self.offers[int(channel_id)] = [
                        Offer(None, offer['user_id'], offer['offer_type'], offer['price'])
                        for offer in offers
                        if offer['active']  # Only load active offers
                    ]
            except (json.JSONDecodeError, FileNotFoundError):
                self.offers = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.author.bot or
                isinstance(message.channel, discord.DMChannel) or
                message.channel.id in self.finished_horses):
            return

        # Check if the channel is a horse channel
        if str(message.channel.id) not in self.horse_channels:
            # Check if the message looks like a trading command
            offer_type, price = self.parse_offer(message.content)
            if offer_type is not None:
                await message.reply("⚠️ This channel is not set up for horse trading. An admin needs to use `!sethorsechannel` to enable trading here.")
            return

        # Handle cancellation
        if await self.handle_cancellation(message):
            return

        # Parse offer
        offer_type, price = self.parse_offer(message.content)
        if offer_type is None:
            return await message.add_reaction("❌")

        await message.add_reaction("🆗")

        # Create new offer
        new_offer = Offer(message, message.author.id, offer_type, price)

        # Initialize channel offers if needed
        if message.channel.id not in self.offers:
            self.offers[message.channel.id] = []

        # Try to find matching offer
        match_offer = self.find_matching_offer(message.channel.id, offer_type, price)

        if match_offer:
            await self.process_transaction(message, match_offer, offer_type, price)
        else:
            self.offers[message.channel.id].append(new_offer)

    @staticmethod
    def parse_offer(content: str) -> Tuple[Optional[str], Optional[int]]:
        match = re.match(r"^(buy|sell)\s+(\d{1,2})$", content.strip().lower())
        if not match:
            return None, None

        offer_type, price = match.groups()
        price = int(price)

        if 5 <= price <= 99:
            return offer_type, price
        return None, None

    async def handle_cancellation(self, message: discord.Message) -> bool:
        if not message.reference or message.content.lower().strip() != "cancel":
            return False

        ref_msg_id = message.reference.message_id
        channel_offers = self.offers.get(message.channel.id, [])

        for offer in channel_offers:
            if (offer.message.id == ref_msg_id and
                    offer.user_id == message.author.id and
                    offer.active):
                offer.active = False
                await offer.message.clear_reactions()
                await offer.message.add_reaction("🚫")
                await message.add_reaction("✅")
                return True

        await message.add_reaction("❌")
        return True

    def find_matching_offer(self, channel_id: int, offer_type: str, price: int) -> Optional[Offer]:
        channel_offers = self.offers.get(channel_id, [])
        opposite = 'sell' if offer_type == 'buy' else 'buy'
        candidates = [o for o in channel_offers if o.offer_type == opposite and o.active]

        if offer_type == 'buy':
            matching = [o for o in candidates if o.price <= price]
            matching.sort(key=lambda o: (o.price, o.message.created_at))
        else:
            matching = [o for o in candidates if o.price >= price]
            matching.sort(key=lambda o: (-o.price, o.message.created_at))

        return matching[0] if matching else None

    async def process_transaction(self, message: discord.Message, match_offer: Offer, offer_type: str, price: int) -> None:
        match_offer.active = False
        buyer_id = message.author.id if offer_type == 'buy' else match_offer.user_id
        seller_id = match_offer.user_id if offer_type == 'buy' else message.author.id
        final_price = match_offer.price

        if message.author.id != match_offer.user_id:
            accepts = self.trading_manager.record_accept(message.author.id)
            if accepts > self.trading_manager.ACCEPT_LIMIT:
                data = self.trading_manager.get_user_data(message.author.id)
                if data['garnets'] > 0:
                    data['garnets'] -= 1
                else:
                    data['money'] -= self.trading_manager.FINE_AMOUNT

        self.trading_manager.apply_transaction(buyer_id, seller_id, final_price, message.channel.id)

        await message.clear_reactions()
        await match_offer.message.clear_reactions()
        await message.add_reaction('✅')
        await match_offer.message.add_reaction('✅')

        flag_emoji = self.emoji_manager.get_unique_flag()
        await message.add_reaction(flag_emoji)
        await match_offer.message.add_reaction(flag_emoji)

        await message.reply(
            f"✅ Transaction #{self.transaction_counter:02} {flag_emoji}: "
            f"<@{buyer_id}> buys from <@{seller_id}> for ${final_price}"
        )

        try:
            logchannel = self.bot.get_channel(int(self.logchannel))
            first_msg_link = f"https://discord.com/channels/{message.guild.id}/{match_offer.message.channel.id}/{match_offer.message.id}"
            second_msg_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
            await logchannel.send(
                f"## {message.channel.name} Transaction #{self.transaction_counter:02} {flag_emoji}\n "
                f"<@{buyer_id}> buys from <@{seller_id}> for ${final_price}\n"
                f"-# [Jump to first message]({first_msg_link}) | [Jump to second message]({second_msg_link})"
            )
        except Exception as e:
            print(f"Failed to send log message: {e}")

        self.transaction_counter += 1
        config = load_config()
        config["trade_counter"] = self.transaction_counter
        save_config(config)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Trading(bot))