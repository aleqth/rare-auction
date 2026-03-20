from datetime import datetime
from agents.base import Agent
from state import get_active_auctions
from config import PALETTES


class CuratorAgent(Agent):
    role = "curator"

    def score(self, request: dict, auction: dict) -> int:
        sc = 0
        req_emotion = request.get("emotion", "")
        req_color = request.get("color", "")
        auction_emotion = auction.get("emotion", "")
        auction_palette = auction.get("palette", "")

        if req_emotion == auction_emotion:
            sc += 3
        if req_color == auction_palette:
            sc += 3

        # Partial keyword matching
        palette_info = PALETTES.get(auction_palette, {})
        for kw in palette_info.get("keywords", []):
            if kw in request.get("text", "").lower():
                sc += 1

        return sc

    def tick(self, state: dict) -> dict:
        requests = [r for r in state.get("collector_requests", []) if not r.get("matched")]
        active = get_active_auctions(state)

        if not requests or not active:
            return state

        for req in requests:
            best_score = 0
            best_auction = None

            for auction in active:
                sc = self.score(req, auction)
                if sc > best_score:
                    best_score = sc
                    best_auction = auction

            if best_auction and best_score >= 2:
                req["matched"] = True
                state.setdefault("matched_requests", []).append({
                    "request_id": req["id"],
                    "request_text": req["text"],
                    "auction_sigil": best_auction["sigil"],
                    "auction_token_id": best_auction["token_id"],
                    "score": best_score,
                    "emotion": best_auction.get("emotion"),
                    "palette": best_auction.get("palette"),
                    "ts": datetime.now().isoformat(),
                    "acted": False,
                })
                self.log(state, "matched",
                         f"'{req['text']}' → token #{best_auction['token_id']} (score={best_score})")
            else:
                self.log(state, "no_match", f"'{req['text']}' — nothing good enough")

        return state
