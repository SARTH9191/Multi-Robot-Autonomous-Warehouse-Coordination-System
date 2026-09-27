"""
WebSocket Manager & Live Stream Endpoint
Streams warehouse simulation state at 20-25 FPS to all connected clients.
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Set
import asyncio
import json
import logging
from .routes import get_coordinator

logger = logging.getLogger("warehouse.ws")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
        dead = []
        payload = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.active_connections.discard(d)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    coord = get_coordinator()
    
    # Send initial state immediately upon connection
    await websocket.send_text(json.dumps({
        "type": "INIT_STATE",
        "data": coord.get_state()
    }))

    try:
        while True:
            # Listen for client command messages
            data = await websocket.receive_text()
            try:
                cmd = json.loads(data)
                action = cmd.get("action")
                
                if action == "START":
                    coord.is_running = True
                elif action == "PAUSE":
                    coord.is_running = False
                elif action == "STEP":
                    coord.is_running = False
                    coord.step()
                elif action == "RESET":
                    coord.load_scenario(coord.current_scenario_id)
                elif action == "SPEED":
                    val = float(cmd.get("value", 1.0))
                    coord.speed_multiplier = max(0.25, min(4.0, val))
                elif action == "LOAD_SCENARIO":
                    sc_id = cmd.get("scenario_id", "SCENARIO_1")
                    coord.load_scenario(sc_id)
                    
                # Broadcast immediately after handling command
                await manager.broadcast({
                    "type": "STATE_UPDATE",
                    "data": coord.get_state()
                })
            except Exception as e:
                logger.error(f"Error handling WS message: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
