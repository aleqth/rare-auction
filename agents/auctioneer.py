from datetime import datetime
from pathlib import Path
from agents.base import Agent
import artwork
import rare_cli
from config import CHAIN, MIN_PRICE, AUCTION_DURATION, BIDDER_WALLET_ADDR, MAIN_WALLET_KEY


class AuctioneerAgent(Agent):
    role = "auctioneer"

    def tick(self, state: dict) -> dict:
        # 1. List pending canvases
        pending = state.get("pending_auctions", [])
        still_pending = []

        for item in pending:
            contract = item["contract"]
            token_id = item["token_id"]
            price = MIN_PRICE

            self.log(state, "listing", f"Canvas #{token_id} at {price} ETH")

            result = rare_cli.auction_create(contract, token_id, price, AUCTION_DURATION, CHAIN)

            if result["success"]:
                auction = {
                    "sigil": item["sigil"],
                    "contract": contract,
                    "token_id": token_id,
                    "starting_price": price,
                    "duration": AUCTION_DURATION,
                    "chain": CHAIN,
                    "created_at": datetime.now().isoformat(),
                    "state": "RUNNING",
                    "bg_color": item.get("bg_color", "#0D0D0D"),
                    "slots": item.get("slots", {"1": None, "2": None, "3": None}),
                    "bids": [],
                    "bid_history": [],
                }
                state.setdefault("auctions", []).append(auction)
                self.log(state, "listed", f"Canvas #{token_id} at {price} ETH")
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

            # Generate final composed artwork
            try:
                composed_path = artwork.generate_composed(
                    auction.get("bg_color", "#0D0D0D"),
                    auction.get("slots", {})
                )
                Path(composed_path).unlink(missing_ok=True)
            except Exception:
                pass

            capsule = {
                "type": "auction_capsule",
                "canvas": token_id,
                "bg_color": auction.get("bg_color"),
                "final_slots": auction.get("slots"),
                "bid_count": len(auction.get("bid_history", [])),
                "bid_history": auction.get("bid_history", []),
                "contract": contract,
                "chain": CHAIN,
                "settled_at": auction["settled_at"],
                "protocol": "RARE/SuperRare",
            }
            state.setdefault("capsules", []).append(capsule)
            self.log(state, "settled", f"Canvas #{token_id} — {len(auction.get('bid_history', []))} bids — capsule emitted")

            # Recycle ETH: top up bidder wallet
            try:
                from web3 import Web3
                w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
                main_acct = w3.eth.account.from_key(MAIN_WALLET_KEY)
                main_bal = w3.eth.get_balance(main_acct.address)
                topup = min(w3.to_wei(0.0005, "ether"), main_bal // 3)
                if topup > w3.to_wei(0.00005, "ether") and BIDDER_WALLET_ADDR:
                    nonce = w3.eth.get_transaction_count(main_acct.address)
                    block = w3.eth.get_block("latest")
                    tx = {
                        "nonce": nonce, "to": BIDDER_WALLET_ADDR,
                        "value": topup, "gas": 21000,
                        "maxFeePerGas": block["baseFeePerGas"] * 3,
                        "maxPriorityFeePerGas": w3.to_wei(0.001, "gwei"),
                        "chainId": 8453, "type": 2,
                    }
                    signed = main_acct.sign_transaction(tx)
                    w3.eth.send_raw_transaction(signed.raw_transaction)
                    rare_cli.configure_wallet(MAIN_WALLET_KEY, CHAIN)
                    self.log(state, "recycled", f"topped up bidder with {w3.from_wei(topup, 'ether')} ETH")
            except Exception as e:
                self.log(state, "recycle_failed", str(e)[:100])

        return state
