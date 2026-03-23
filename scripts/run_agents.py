#!/usr/bin/env python3
"""
Autonomous auction loop. Artist mints canvas, auctioneer lists, bidders choose colors for slots.
Each bid reshapes the artwork. The final settled piece = sum of all bids.
"""
import sys
import time
import signal

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

import state as state_mod
from config import CONTRACTS, AGENT_LOOP_INTERVAL, BIDDER_PROFILES
from agents import ArtistAgent, AuctioneerAgent, BidderAgent

running = True


def shutdown(sig, frame):
    global running
    print("\nShutting down agents...")
    running = False


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


def main():
    artist = ArtistAgent({"role": "artist", **CONTRACTS["artist"]})
    auctioneer = AuctioneerAgent({"role": "auctioneer", **CONTRACTS["auctioneer"]})
    bidders = [
        BidderAgent({"role": "bidder", **CONTRACTS["bidder"]}, profile)
        for profile in BIDDER_PROFILES
    ]

    print("=== Autonomous Agent Auction (Collaborative) ===")
    print(f"Artist:     {artist.sigil} {artist.name}")
    print(f"Auctioneer: {auctioneer.sigil} {auctioneer.name}")
    for b in bidders:
        print(f"Bidder:     {b.bidder_name} → slot {b.slot_pref}, colors {b.color_prefs[:2]}...")
    print(f"Loop interval: {AGENT_LOOP_INTERVAL}s")
    print("================================================\n")

    while running:
        s = state_mod.load()
        cycle = s.get("cycle_count", 0) + 1
        s["cycle_count"] = cycle
        print(f"\n--- Cycle {cycle} ---")

        # 1. Artist mints (only if no active auction)
        try:
            s = artist.tick(s)
            state_mod.save(s)
        except Exception as e:
            print(f"[artist error] {e}")

        # 2. Auctioneer lists + settles
        try:
            s = auctioneer.tick(s)
            state_mod.save(s)
        except Exception as e:
            print(f"[auctioneer error] {e}")

        # 3. Each bidder bids with color choices
        for bidder in bidders:
            try:
                s = bidder.tick(s)
                state_mod.save(s)
            except Exception as e:
                print(f"[{bidder.bidder_name} error] {e}")

        state_mod.save(s)
        print(f"--- Cycle {cycle} complete. Sleeping {AGENT_LOOP_INTERVAL}s ---")

        for _ in range(AGENT_LOOP_INTERVAL):
            if not running:
                break
            time.sleep(1)

    print("Agents stopped.")


if __name__ == "__main__":
    main()
