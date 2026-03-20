import random
from datetime import datetime
from agents.base import Agent
import rare_cli
from config import CHAIN, EMOTIONS, PALETTES


class CollectorAgent(Agent):
    role = "collector"

    def generate_desire(self) -> dict:
        emotion = random.choice(EMOTIONS)
        palette_name = random.choice(list(PALETTES.keys()))
        text = f"I want a {emotion} {palette_name} piece"
        return {
            "id": f"req_{int(datetime.now().timestamp())}_{random.randint(0,999)}",
            "text": text,
            "emotion": emotion,
            "color": palette_name,
            "matched": False,
            "ts": datetime.now().isoformat(),
        }

    def tick(self, state: dict) -> dict:
        # 1. Generate a new desire
        desire = self.generate_desire()
        state.setdefault("collector_requests", []).append(desire)
        self.log(state, "wants", desire["text"])

        # 2. Check matched requests and bid
        matched = state.get("matched_requests", [])
        acted = []

        for match in matched:
            if match.get("acted"):
                continue

            auction = None
            for a in state.get("auctions", []):
                if a["sigil"] == match["auction_sigil"] and a["token_id"] == match["auction_token_id"] and a["state"] == "RUNNING":
                    auction = a
                    break

            if not auction:
                continue

            bid_amount = round(auction["starting_price"] * random.uniform(1.0, 1.5), 4)
            result = rare_cli.auction_bid(auction["contract"], auction["token_id"], bid_amount, CHAIN)

            if result["success"]:
                auction.setdefault("bids", []).append({
                    "bidder": f"{self.sigil} collector",
                    "amount": bid_amount,
                    "ts": datetime.now().isoformat(),
                })
                match["acted"] = True
                self.log(state, "bid", f"{bid_amount} ETH on token #{auction['token_id']}")
            else:
                self.log(state, "bid_failed", result["error"][:200])

        return state
