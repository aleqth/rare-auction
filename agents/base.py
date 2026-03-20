import state as state_mod


class Agent:
    role: str = ""
    sigil: str = ""
    name: str = ""
    contract: str = ""

    def __init__(self, role_config: dict):
        self.role = role_config.get("role", self.role)
        self.sigil = role_config.get("sigil", "")
        self.name = role_config.get("name", "")
        self.contract = role_config.get("contract", "")

    def tick(self, state: dict) -> dict:
        raise NotImplementedError

    def log(self, state: dict, action: str, detail: str):
        state_mod.add_event(state, f"{self.sigil} {self.role}", action, detail)
        print(f"[{self.sigil} {self.role}] {action}: {detail}")
