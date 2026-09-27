"""
Main FastAPI Server for Autonomous Warehouse Multi-Robot Coordinator
Provides REST endpoints and WebSocket stream for real-time frontend visualization.
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from .api.routes import router, get_coordinator
from .api.websocket import websocket_endpoint, manager

ticker_task = None

async def simulation_ticker_loop():
    """
    Background simulation clock.
    Steps simulation when running and broadcasts state over WebSockets at ~25 Hz.
    """
    coord = get_coordinator()
    while True:
        try:
            if coord.is_running:
                coord.step()
                if len(manager.active_connections) > 0:
                    await manager.broadcast({
                        "type": "STATE_UPDATE",
                        "data": coord.get_state()
                    })
            await asyncio.sleep(0.04) # ~25 ticks per second
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in simulation ticker: {e}")
            await asyncio.sleep(0.1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ticker_task
    ticker_task = asyncio.create_task(simulation_ticker_loop())
    print("Warehouse Simulation Ticker started.")
    yield
    if ticker_task:
        ticker_task.cancel()
        try:
            await ticker_task
        except asyncio.CancelledError:
            pass
    print("Warehouse Simulation Ticker stopped.")

app = FastAPI(
    title="Autonomous Warehouse Multi-Robot Coordination System",
    description="DAA Capstone Project: Multi-Robot AGV Coordination with A*, DP-TSP, Geometry Collision Detection, and Greedy Scheduling.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.websocket("/ws")
async def ws_route(websocket: WebSocket):
    await websocket_endpoint(websocket)

@app.get("/")
def root_status():
    return {
        "status": "online",
        "service": "Autonomous Warehouse Multi-Robot Coordinator Backend",
        "algorithms": ["BFS", "DFS", "A*", "DP-TSP", "Geometry", "Collision", "Greedy Scheduler"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
