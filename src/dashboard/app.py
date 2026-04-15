"""
RL Firewall Dashboard - Real-time Web Interface
Usage: python -m uvicorn src.dashboard.app:app --reload --port 8080
"""
import asyncio
import json
import time
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from src.dashboard.database import db

app = FastAPI(title="RL Firewall Dashboard")
templates = Jinja2Templates(directory="src/dashboard/templates")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and wait for any messages (ping/pong)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task to broadcast updates
async def broadcast_updates():
    """Broadcast real-time updates to all connected clients every 2 seconds"""
    while True:
        try:
            stats = db.get_stats()
            await manager.broadcast({
                "type": "stats_update",
                "data": stats,
                "timestamp": time.time()
            })
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Broadcast error: {e}")
            await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_updates())
