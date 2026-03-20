from pathlib import Path
from agents.base import Agent
import artwork
import rare_cli
from config import CHAIN, EMOTION_SYMBOLS


class ArtistAgent(Agent):
    role = "artist"

    def tick(self, state: dict) -> dict:
        traits = artwork.pick_traits()
        emotion = traits["emotion"]
        palette = traits["palette_name"]
        palette_hex = traits["palette_hex"]
        seed = traits["seed"]

        self.log(state, "creating", f"emotion={emotion} palette={palette} seed={seed}")

        image_path = artwork.generate(emotion, palette_hex, seed)

        agent_state = state["agents"].get(self.sigil, {})
        contract = agent_state.get("contract", self.contract)
        token_num = agent_state.get("next_token_id", 1)
        token_name = f"{self.sigil} {self.name} #{token_num:03d}"
        description = f"Autonomous agent artwork. Emotion: {emotion} {EMOTION_SYMBOLS[emotion]}. Palette: {palette}."

        attributes = [
            ("Emotion", emotion),
            ("EmotionSymbol", EMOTION_SYMBOLS[emotion]),
            ("Palette", palette_hex),
            ("PaletteName", palette),
            ("Agent", self.name),
            ("Sigil", self.sigil),
            ("Seed", str(seed)),
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
                "emotion": emotion,
                "palette": palette,
                "palette_hex": palette_hex,
                "seed": seed,
            })

            self.log(state, "minted", f"token #{token_id} — {emotion} {EMOTION_SYMBOLS[emotion]} / {palette}")
        else:
            self.log(state, "mint_failed", result["error"][:200])

        return state
