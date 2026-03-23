import random
from pathlib import Path
from agents.base import Agent
import artwork
import rare_cli
from config import CHAIN, CANVAS_BG_COLORS
from state import get_active_auctions


class ArtistAgent(Agent):
    role = "artist"

    def tick(self, state: dict) -> dict:
        # Only mint if no active auction — one canvas at a time
        if get_active_auctions(state):
            return state

        bg_color = random.choice(CANVAS_BG_COLORS)
        self.log(state, "creating", f"canvas with background {bg_color}")

        image_path = artwork.generate_canvas(bg_color)

        agent_state = state["agents"].get(self.sigil, {})
        contract = agent_state.get("contract", self.contract)
        token_num = agent_state.get("next_token_id", 1)
        token_name = f"Canvas #{token_num:03d}"
        description = f"Blank canvas. Background: {bg_color}. Slots shaped by bidders."

        attributes = [
            ("Background", bg_color),
            ("Slots", "3"),
            ("Agent", "artist"),
        ]

        result = rare_cli.mint(contract, token_name, description, image_path, CHAIN, attributes)

        try:
            Path(image_path).unlink(missing_ok=True)
        except Exception:
            pass

        if result["success"]:
            token_id = result.get("token_id", token_num)
            agent_state["next_token_id"] = token_num + 1
            agent_state.setdefault("minted_tokens", []).append(token_id)
            state["agents"][self.sigil] = agent_state

            state.setdefault("pending_auctions", []).append({
                "sigil": self.sigil,
                "contract": contract,
                "token_id": token_id,
                "bg_color": bg_color,
                "slots": {"1": None, "2": None, "3": None},
            })

            self.log(state, "minted", f"Canvas #{token_id} — background {bg_color}")
        else:
            self.log(state, "mint_failed", result["error"][:200])

        return state
