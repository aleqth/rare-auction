import os
from dotenv import load_dotenv

load_dotenv()

CHAIN = os.getenv("RARE_CHAIN", "base")
RARE_BIN = os.getenv("RARE_BIN", "rare")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8899"))
AGENT_LOOP_INTERVAL = int(os.getenv("AGENT_LOOP_INTERVAL", "180"))
AUCTION_DURATION = int(os.getenv("AUCTION_DURATION", "3600"))
MIN_PRICE = float(os.getenv("MIN_PRICE", "0.0001"))
STATE_FILE = os.path.expanduser("~/.rare/ankle_state.json")

CANVAS_BG_COLORS = ["#0D0D0D", "#1A0A2E", "#0A1628", "#1C1C1C", "#0A0A14", "#12000A", "#001A0A"]

BIDDER_PROFILES = [
    {"id": "nyx",    "name": "Nyx",    "color_prefs": ["#1A0A2E", "#0A1628", "#12000A", "#0D0D2A", "#1C0A1C"], "slot_pref": 0},
    {"id": "mira",   "name": "Mira",   "color_prefs": ["#FF6B6B", "#FF3B30", "#E74C3C", "#C0392B"], "slot_pref": 1},
    {"id": "sol",    "name": "Sol",    "color_prefs": ["#4ECDC4", "#00C98D", "#1ABC9C", "#2ECC71"], "slot_pref": 2},
    {"id": "vesper", "name": "Vesper", "color_prefs": ["#FFD93D", "#FF8C42", "#F39C12", "#E67E22"], "slot_pref": 3},
]

CONTRACTS = {
    "artist":     {"sigil": "◈", "name": "Protocol Designer", "contract": "0x2800C1B441CA9f06Ebb7e75e976d318BAeaC2774"},
    "auctioneer": {"sigil": "◎", "name": "Commercialization Lead", "contract": "0xd53db84F5119F2e6DFc75C2aBC1221424cec7cD3"},
    "bidder":     {"sigil": "⟡", "name": "User Advocate", "contract": "0x868C7aBF093CB9CD89A0F0DdeF4118A65438807A"},
}

SHARED_WALLET = "0x005e84c1e700ea929CE826aC41d39302980C772E"
BIDDER_WALLET_KEY = os.getenv("BIDDER_WALLET_KEY", "")
BIDDER_WALLET_ADDR = os.getenv("BIDDER_WALLET_ADDR", "")
MAIN_WALLET_KEY = os.getenv("PRIVATE_KEY", "")
