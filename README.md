# Autonomous Agent Auction

Autonomous agents that live, mint, auction, and settle entirely onchain using [Rare Protocol CLI](https://github.com/superrare/rare-cli). Agent behavior and marketplace state become the artwork itself.

Built for the [SuperRare Partner Track](https://synthesis.md/hack/#superrare) — Synthesis 2026.

## How It Works

4 autonomous agents run in a continuous loop with no human intervention:

| Agent | Role | What It Does |
|-------|------|-------------|
| **Artist** | Creates artwork | Generates images with RNG traits (emotion + palette), mints via `rare mint` |
| **Auctioneer** | Prices + settles | Suggests price based on emotion traits, lists via `rare auction create`, settles expired auctions |
| **Collector** | Desires + bids | Generates random requests ("I want a sad blue piece"), bids via `rare auction bid` |
| **Curator** | Matches | Scores active auctions against collector requests, tells collectors what to bid on |

### The Artwork

Each piece is generated with two traits:
- **Emotion**: happy `:)`, sad `:(`, anger `>:(`, love `<3`, lust `~`
- **Palette**: blue, orange, green, purple, gold, red, cyan

The artwork visually transforms through the auction lifecycle:
1. **Minted** — background fills with palette color
2. **Listed** — slot 1 unlocks
3. **Bid received** — slot 2 unlocks
4. **Settled** — slot 3 unlocks, DSEP capsule emitted

The visual format follows the [dada](https://aleqth.com/dada) template: 768x987 canvas with 3 vertically stacked slots.

### Agent Loop (one cycle)

```
Artist picks traits → generates image → mints onchain
    ↓
Auctioneer prices based on emotion → lists auction
    ↓
Collector generates desire → "I want a sad blue piece"
    ↓
Curator matches desire to active auctions
    ↓
Collector bids on matched auction
    ↓
Auctioneer settles expired auctions → emits DSEP capsule
    ↓
sleep(AGENT_LOOP_INTERVAL) → repeat
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js 22+
- [Rare Protocol CLI](https://www.npmjs.com/package/@rareprotocol/rare-cli)

### Install

```bash
git clone https://github.com/YOUR_USERNAME/rare-auction.git
cd rare-auction
pip install -r requirements.txt
npm install -g @rareprotocol/rare-cli
```

### Configure

```bash
cp .env.example .env
# Edit .env with your private key and rare CLI path
```

Configure the Rare CLI:
```bash
rare configure --chain base --private-key YOUR_PRIVATE_KEY
rare wallet address --chain base  # verify
```

### Run

Terminal 1 — start the server:
```bash
python server.py
```

Terminal 2 — start the agents:
```bash
python scripts/run_agents.py
```

Visit `http://localhost:8899` to see the live dashboard.

## Deployed Contracts (Base Mainnet)

| Role | Contract |
|------|----------|
| Artist (Protocol Designer) | [`0x2800...2774`](https://basescan.org/address/0x2800C1B441CA9f06Ebb7e75e976d318BAeaC2774) |
| Auctioneer (Commercialization Lead) | [`0xd53d...7cD3`](https://basescan.org/address/0xd53db84F5119F2e6DFc75C2aBC1221424cec7cD3) |
| Collector (User Advocate) | [`0x868C...807A`](https://basescan.org/address/0x868C7aBF093CB9CD89A0F0DdeF4118A65438807A) |
| Curator (Data Steward) | [`0x29F0...0287`](https://basescan.org/address/0x29F0e9942E7631b1475316066Ebb93a1f3660287) |

## Architecture

```
rare-auction/
  config.py          — all configuration, traits, contracts
  state.py           — JSON state management
  rare_cli.py        — subprocess wrapper for rare CLI
  artwork.py         — procedural image generation (Pillow)
  server.py          — FastAPI server + frontend
  agents/
    base.py          — base agent class
    artist.py        — mints artwork with RNG traits
    auctioneer.py    — prices, lists, settles auctions
    collector.py     — generates desires, bids
    curator.py       — matches desires to auctions
  frontend/
    index.html       — SuperRare-style live dashboard
  scripts/
    run_agents.py    — autonomous agent loop (no human intervention)
```

## DSEP Capsule

Every settled auction emits a capsule — a provenance record that captures the full lifecycle:

```json
{
  "type": "auction_capsule",
  "artist": { "sigil": "◈", "emotion": "sad", "palette": "#1E4DFF" },
  "contract": "0x2800...",
  "token_id": 1,
  "chain": "base",
  "bids": [{ "bidder": "⟡ collector", "amount": 0.0013 }],
  "settled_at": "2026-03-20T...",
  "protocol": "RARE/SuperRare"
}
```

## Stack

- **Onchain**: Rare Protocol CLI → ERC-721 on Base
- **Images**: Pillow procedural generation, IPFS via Rare CLI
- **Backend**: Python, FastAPI
- **Frontend**: Vanilla HTML/JS, SuperRare-style layout

## License

MIT
