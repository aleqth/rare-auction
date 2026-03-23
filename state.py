import json
from pathlib import Path
from datetime import datetime
from config import STATE_FILE

_state_path = Path(STATE_FILE)


def load() -> dict:
    try:
        return json.loads(_state_path.read_text())
    except Exception:
        return _default()


def save(state: dict):
    _state_path.parent.mkdir(parents=True, exist_ok=True)
    _state_path.write_text(json.dumps(state, indent=2))


def _default() -> dict:
    return {
        "shared_wallet": "",
        "chain": "base",
        "agents": {},
        "auctions": [],
        "capsules": [],
        "pending_auctions": [],
        "events": [],
        "cycle_count": 0,
    }


def get_active_auctions(state: dict) -> list:
    return [a for a in state.get("auctions", []) if a.get("state") == "RUNNING"]


def get_expired_auctions(state: dict) -> list:
    now = datetime.now()
    expired = []
    for a in state.get("auctions", []):
        if a.get("state") != "RUNNING":
            continue
        created = datetime.fromisoformat(a["created_at"])
        if (now - created).total_seconds() >= a.get("duration", 3600):
            expired.append(a)
    return expired


def get_current_artwork(state: dict) -> dict:
    """Get the current artwork state for the frontend."""
    auctions = state.get("auctions", [])
    # Prefer active auction, fallback to latest settled
    active = [a for a in auctions if a.get("state") == "RUNNING"]
    if active:
        a = active[-1]
        return {
            "bg_color": a.get("bg_color", "#0D0D0D"),
            "slots": a.get("slots", {"1": None, "2": None, "3": None}),
            "bid_history": a.get("bid_history", []),
            "auction_state": "RUNNING",
            "token_id": a.get("token_id"),
        }
    if auctions:
        a = auctions[-1]
        return {
            "bg_color": a.get("bg_color", "#0D0D0D"),
            "slots": a.get("slots", {"1": None, "2": None, "3": None}),
            "bid_history": a.get("bid_history", []),
            "auction_state": a.get("state", "SETTLED"),
            "token_id": a.get("token_id"),
        }
    return {"bg_color": "#0D0D0D", "slots": {"1": None, "2": None, "3": None}, "bid_history": [], "auction_state": "IDLE", "token_id": None}


def add_event(state: dict, agent: str, action: str, detail: str):
    state.setdefault("events", []).append({
        "ts": datetime.now().isoformat(),
        "agent": agent,
        "action": action,
        "detail": detail,
    })
    if len(state["events"]) > 500:
        state["events"] = state["events"][-500:]
