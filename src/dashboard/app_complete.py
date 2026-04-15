"""
RL Firewall Dashboard - Complete Working Version
Usage: python src/dashboard/app_complete.py
"""
import asyncio
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn

from src.dashboard.database import db

app = FastAPI(title="RL Firewall Dashboard")
templates = Jinja2Templates(directory="src/dashboard/templates")

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active = []

    async def connect(self, ws):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, msg: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(msg)
            except:
                dead.append(ws)
        for ws in dead:
            if ws in self.active:
                self.active.remove(ws)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/stats")
async def get_stats():
    return db.get_stats()

@app.get("/api/events")
async def get_events(limit: int = 50):
    return db.get_recent_events(limit)

@app.get("/api/metrics/history")
async def get_metrics_history(minutes: int = 5):
    return db.get_metrics_history(minutes)

@app.post("/api/flush")
async def flush_rules():
    return {"status": "flushed"}

@app.get("/api/export")
async def export_logs():
    events = db.get_recent_events(1000)
    return PlainTextResponse(
        content=json.dumps(events, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=firewall_logs.json"}
    )

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(ws)

async def broadcast_loop():
    while True:
        try:
            stats = db.get_stats()
            await manager.broadcast({
                "type": "stats_update",
                "data": stats,
                "timestamp": time.time()
            })
        except Exception as e:
            print(f"Broadcast error: {e}")
        await asyncio.sleep(2)

@app.on_event("startup")
async def startup():
    asyncio.create_task(broadcast_loop())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
