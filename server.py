#!/usr/bin/env python3
"""
FastAPI server — serves the frontend and exposes state/events API.
Read-only for state (agents write via run_agents.py).
"""
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

import state as state_mod
from config import SERVER_PORT

app = FastAPI(title="Autonomous Agent Auction")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

FRONTEND = Path(__file__).parent / "frontend" / "index.html"


@app.get("/")
async def serve_frontend():
    return FileResponse(str(FRONTEND), headers={"Cache-Control": "no-store"})


@app.get("/api/state")
async def get_state():
    s = state_mod.load()
    # Redact private keys if any
    safe_agents = {}
    for sigil, agent in s.get("agents", {}).items():
        safe_agents[sigil] = {k: v for k, v in agent.items() if k != "private_key"}
    return JSONResponse({**s, "agents": safe_agents})


@app.get("/api/events")
async def get_events():
    s = state_mod.load()
    return JSONResponse(s.get("events", [])[-100:])


@app.get("/api/auctions")
async def get_auctions():
    s = state_mod.load()
    return JSONResponse(s.get("auctions", []))


@app.get("/api/auctions/active")
async def get_active_auctions():
    s = state_mod.load()
    return JSONResponse(state_mod.get_active_auctions(s))


@app.get("/api/capsules")
async def get_capsules():
    s = state_mod.load()
    return JSONResponse(s.get("capsules", []))


@app.get("/api/cycle")
async def get_cycle():
    s = state_mod.load()
    return JSONResponse({"cycle": s.get("cycle_count", 0)})


if __name__ == "__main__":
    print(f"Server starting on http://0.0.0.0:{SERVER_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT, log_level="warning")
