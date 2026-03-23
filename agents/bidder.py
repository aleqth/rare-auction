import random
from datetime import datetime
from agents.base import Agent
import rare_cli
from config import CHAIN, BIDDER_WALLET_KEY, MAIN_WALLET_KEY
from state import get_active_auctions


class BidderAgent(Agent):
    role = "bidder"

    def __init__(self, role_config: dict, profile: dict):
        super().__init__(role_config)
        self.bidder_id = profile["id"]
        self.bidder_name = profile["name"]
        self.color_prefs = profile["color_prefs"]
        self.slot_pref = profile.get("slot_pref")

    def choose_color_and_slot(self) -> tuple:
        slot = self.slot_pref if self.slot_pref is not None else random.randint(0, 3)
        base_color = random.choice(self.color_prefs)
        # Add jitter so each bid looks unique
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        r = max(0, min(255, r + random.randint(-20, 20)))
        g = max(0, min(255, g + random.randint(-20, 20)))
        b = max(0, min(255, b + random.randint(-20, 20)))
        color = f"#{r:02x}{g:02x}{b:02x}"
        return slot, color

    def tick(self, state: dict) -> dict:
        active = get_active_auctions(state)
        if not active:
            return state

        for auction in active:
            # 60% chance to bid per cycle — creates organic timing
            if random.random() > 0.6:
                continue

            slot, color = self.choose_color_and_slot()

            # Bid amount: starting price + small increment
            existing_bids = auction.get("bids", [])
            if existing_bids:
                highest = max(float(b.get("amount", 0)) for b in existing_bids)
                bid_amount = round(highest * random.uniform(1.05, 1.2), 5)
            else:
                bid_amount = round(auction["starting_price"] * random.uniform(1.1, 1.5), 5)

            self.log(state, "bidding", f"{self.bidder_name} choosing {color} for slot {slot} ({bid_amount} ETH)")

            result = rare_cli.auction_bid(
                auction["contract"], auction["token_id"],
                bid_amount, CHAIN, bidder_key=BIDDER_WALLET_KEY
            )
            # Restore main wallet
            rare_cli.configure_wallet(MAIN_WALLET_KEY, CHAIN)

            if result["success"]:
                # Update slot color
                auction.setdefault("slots", {"1": None, "2": None, "3": None})
                auction["slots"][str(slot)] = color

                bid_record = {
                    "bidder_id": self.bidder_id,
                    "bidder_name": self.bidder_name,
                    "slot": slot,
                    "color": color,
                    "amount": bid_amount,
                    "ts": datetime.now().isoformat(),
                }
                auction.setdefault("bids", []).append(bid_record)
                auction.setdefault("bid_history", []).append(bid_record)

                slot_label = "background" if slot == 0 else f"slot {slot}"
                self.log(state, "bid", f"{self.bidder_name} set {slot_label} to {color} ({bid_amount} ETH)")
            else:
                self.log(state, "bid_failed", result["error"][:150])

        return state
