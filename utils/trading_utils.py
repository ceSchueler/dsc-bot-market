from dataclasses import dataclass
from typing import Dict, Any

import discord


@dataclass
class Offer:
    """
    Represents a trading offer in the system
    """
    message: discord.Message
    user_id: int
    offer_type: str
    price: int
    active: bool = True


class TradingManager:
    """
    Manages trading-related functionality
    """

    def __init__(self):
        self.user_balances: Dict[int, Dict[str, Any]] = {}
        self.user_accepts: Dict[int, Dict[int, int]] = {}
        self.current_round: int = 1
        self.ACCEPT_LIMIT: int = 2
        self.FINE_AMOUNT: int = 100

    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Gets or creates user trading data
        """
        if user_id not in self.user_balances:
            self.user_balances[user_id] = {
                'money': 1000,
                'hype': {},
                'garnets': 3
            }
        return self.user_balances[user_id]

    def record_accept(self, user_id: int) -> int:
        """
        Records a user acceptance and returns the number of accepts in current round
        """
        count = self.user_accepts.setdefault(user_id, {}).setdefault(self.current_round, 0)
        self.user_accepts[user_id][self.current_round] += 1
        return count + 1

    def apply_transaction(
            self,
            buyer_id: int,
            seller_id: int,
            price: int,
            channel_id: int
    ) -> None:
        """
        Applies a transaction between buyer and seller
        """
        buyer = self.get_user_data(buyer_id)
        seller = self.get_user_data(seller_id)

        buyer['money'] -= price
        buyer['hype'][channel_id] = buyer['hype'].get(channel_id, 0) + 1

        seller['money'] += price
        seller['hype'][channel_id] = seller['hype'].get(channel_id, 0) - 1
