#!/usr/bin/env python3
"""
Autonomous agent loop. Runs continuously — no human intervention.
Cycle: artist mints → auctioneer lists → collector desires → curator matches → collector bids → auctioneer settles
"""
import sys
import time
import signal

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

import state as state_mod
from config import CONTRACTS, AGENT_LOOP_INTERVAL
from agents import ArtistAgent, AuctioneerAgent, CollectorAgent, CuratorAgent

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
    collector = CollectorAgent({"role": "collector", **CONTRACTS["collector"]})
    curator = CuratorAgent({"role": "curator", **CONTRACTS["curator"]})

    print("=== Autonomous Agent Auction ===")
    print(f"Artist:     {artist.sigil} {artist.name}")
    print(f"Auctioneer: {auctioneer.sigil} {auctioneer.name}")
    print(f"Collector:  {collector.sigil} {collector.name}")
    print(f"Curator:    {curator.sigil} {curator.name}")
    print(f"Loop interval: {AGENT_LOOP_INTERVAL}s")
    print("================================\n")

    while running:
        state = state_mod.load()
        cycle = state.get("cycle_count", 0) + 1
        state["cycle_count"] = cycle
        print(f"\n--- Cycle {cycle} ---")

        try:
            state = artist.tick(state)
            state_mod.save(state)
        except Exception as e:
            print(f"[artist error] {e}")

        try:
            state = auctioneer.tick(state)
            state_mod.save(state)
        except Exception as e:
            print(f"[auctioneer error] {e}")

        try:
            state = collector.tick(state)
            state_mod.save(state)
        except Exception as e:
            print(f"[collector error] {e}")

        try:
            state = curator.tick(state)
            state_mod.save(state)
        except Exception as e:
            print(f"[curator error] {e}")

        # Collector acts on matches
        try:
            state = collector.tick(state)
            state_mod.save(state)
        except Exception as e:
            print(f"[collector bid error] {e}")

        # Auctioneer settles expired
        try:
            state = auctioneer.tick(state)
            state_mod.save(state)
        except Exception as e:
            print(f"[auctioneer settle error] {e}")

        state_mod.save(state)
        print(f"--- Cycle {cycle} complete. Sleeping {AGENT_LOOP_INTERVAL}s ---")

        for _ in range(AGENT_LOOP_INTERVAL):
            if not running:
                break
            time.sleep(1)

    print("Agents stopped.")


if __name__ == "__main__":
    main()
