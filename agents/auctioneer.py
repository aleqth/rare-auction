import random
from datetime import datetime
from agents.base import Agent
import rare_cli
from config import CHAIN, EMOTION_PRICE_MULTIPLIER, MIN_PRICE, MAX_PRICE, AUCTION_DURATION, COLLECTOR_WALLET_ADDR, MAIN_WALLET_KEY


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

            # Recycle: top up collector wallet from settlement proceeds
            try:
                from web3 import Web3
                w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
                main_acct = w3.eth.account.from_key(MAIN_WALLET_KEY)
                main_bal = w3.eth.get_balance(main_acct.address)
                topup = min(w3.to_wei(0.0005, "ether"), main_bal // 3)
                if topup > w3.to_wei(0.0001, "ether"):
                    nonce = w3.eth.get_transaction_count(main_acct.address)
                    block = w3.eth.get_block("latest")
                    tx = {
                        "nonce": nonce, "to": COLLECTOR_WALLET_ADDR,
                        "value": topup, "gas": 21000,
                        "maxFeePerGas": block["baseFeePerGas"] * 3,
                        "maxPriorityFeePerGas": w3.to_wei(0.001, "gwei"),
                        "chainId": 8453, "type": 2,
                    }
                    signed = main_acct.sign_transaction(tx)
                    w3.eth.send_raw_transaction(signed.raw_transaction)
                    self.log(state, "recycled", f"topped up collector with {w3.from_wei(topup, 'ether')} ETH")
                    # Restore main wallet in rare config
                    rare_cli.configure_wallet(MAIN_WALLET_KEY, CHAIN)
            except Exception as e:
                self.log(state, "recycle_failed", str(e)[:100])

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
