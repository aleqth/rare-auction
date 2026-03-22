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
MAX_PRICE = float(os.getenv("MAX_PRICE", "0.001"))
STATE_FILE = os.path.expanduser("~/.rare/ankle_state.json")

EMOTIONS = ["happy", "sad", "anger", "love", "lust"]

EMOTION_SYMBOLS = {
    "happy": ":)",
    "sad": ":(",
    "anger": ">:(",
    "love": "<3",
    "lust": "~",
}

EMOTION_COLORS = {
    "happy": "#FFD93D",
    "sad": "#4A6FA5",
    "anger": "#FF3B30",
    "love": "#FF6B9D",
    "lust": "#9B59B6",
}

EMOTION_PRICE_MULTIPLIER = {
    "happy": 0.8,
    "sad": 1.1,
    "anger": 1.0,
    "love": 1.3,
    "lust": 1.5,
}

PALETTES = {
    "blue": {"hex": "#1E4DFF", "keywords": ["blue", "cobalt", "azure", "sapphire", "navy", "cold"]},
    "orange": {"hex": "#FF8C42", "keywords": ["orange", "amber", "warm", "fire", "coral"]},
    "green": {"hex": "#00C98D", "keywords": ["green", "emerald", "teal", "mint"]},
    "purple": {"hex": "#6B35D4", "keywords": ["purple", "violet", "indigo", "lavender"]},
    "gold": {"hex": "#FFD700", "keywords": ["gold", "yellow", "golden", "bright"]},
    "red": {"hex": "#CC0000", "keywords": ["red", "crimson", "scarlet", "ruby"]},
    "cyan": {"hex": "#00BFFF", "keywords": ["cyan", "sky", "electric", "neon"]},
}

# Deployed contracts on Base mainnet (from ankle_state.json)
CONTRACTS = {
    "artist": {"sigil": "◈", "name": "Protocol Designer", "contract": "0x2800C1B441CA9f06Ebb7e75e976d318BAeaC2774"},
    "auctioneer": {"sigil": "◎", "name": "Commercialization Lead", "contract": "0xd53db84F5119F2e6DFc75C2aBC1221424cec7cD3"},
    "collector": {"sigil": "⟡", "name": "User Advocate", "contract": "0x868C7aBF093CB9CD89A0F0DdeF4118A65438807A"},
    "curator": {"sigil": "⊛", "name": "Data Steward", "contract": "0x29F0e9942E7631b1475316066Ebb93a1f3660287"},
}

SHARED_WALLET = "0x005e84c1e700ea929CE826aC41d39302980C772E"
COLLECTOR_WALLET_KEY = os.getenv("COLLECTOR_WALLET_KEY", "0xe6f8758ca327499d8e04226003633106b2a684f5a431b7daadebeb3042a7eb6a")
COLLECTOR_WALLET_ADDR = "0xd4F16582548B731e245C46C8CC6D5C107ab6127f"
MAIN_WALLET_KEY = os.getenv("PRIVATE_KEY", "")
