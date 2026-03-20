import random
from datetime import datetime
from agents.base import Agent
import rare_cli
from config import CHAIN, EMOTION_PRICE_MULTIPLIER, MIN_PRICE, MAX_PRICE, AUCTION_DURATION


class AuctioneerAgent(Agent):
    role = "auctioneer"

    def suggest_price(self, emotion: str) -> float:
        base = (MIN_PRICE + MAX_PRICE) / 2
        mult = EMOTION_PRICE_MULTIPLIER.get(emotion, 1.0)
        jitter = random.uniform(0.7, 1.3)
        price = round(base * mult * jitter, 4)
        return max(MIN_PRICE, min(MAX_PRICE, price))

    def tick(self, state: dict) -> dict:
        # 1. List pending auctions
        pending = state.get("pending_auctions", [])
        still_pending = []

        for item in pending:
            emotion = item.get("emotion", "happy")
            price = self.suggest_price(emotion)
            contract = item["contract"]
            token_id = item["token_id"]

            self.log(state, "pricing", f"token #{token_id} — emotion={emotion} → {price} ETH")

            result = rare_cli.auction_create(contract, token_id, price, AUCTION_DURATION, CHAIN)

            if result["success"]:
                auction = {
                    "sigil": item["sigil"],
                    "agent": "artist",
                    "contract": contract,
                    "token_id": token_id,
                    "starting_price": price,
                    "duration": AUCTION_DURATION,
                    "chain": CHAIN,
                    "created_at": datetime.now().isoformat(),
                    "state": "RUNNING",
                    "bids": [],
                    "emotion": emotion,
                    "palette": item.get("palette", ""),
                    "palette_hex": item.get("palette_hex", ""),
                }
                state.setdefault("auctions", []).append(auction)
                self.log(state, "listed", f"token #{token_id} at {price} ETH — {emotion}")
            else:
                self.log(state, "list_failed", result["error"][:200])
                still_pending.append(item)

        state["pending_auctions"] = still_pending

        # 2. Settle expired auctions
        from state import get_expired_auctions
        for auction in get_expired_auctions(state):
            contract = auction["contract"]
            token_id = auction["token_id"]

            result = rare_cli.auction_settle(contract, token_id, CHAIN)
            auction["state"] = "SETTLED"
            auction["settled_at"] = datetime.now().isoformat()

            capsule = {
                "type": "auction_capsule",
                "artist": {"sigil": auction["sigil"], "emotion": auction.get("emotion"), "palette": auction.get("palette_hex")},
                "contract": contract,
                "token_id": token_id,
                "chain": CHAIN,
                "bids": auction.get("bids", []),
                "starting_price": auction.get("starting_price"),
                "settled_at": auction["settled_at"],
                "protocol": "RARE/SuperRare",
            }
            state.setdefault("capsules", []).append(capsule)
            self.log(state, "settled", f"token #{token_id} — capsule emitted")

        return state
