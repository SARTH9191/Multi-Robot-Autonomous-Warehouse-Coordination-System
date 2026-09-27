"""
HTTP REST Endpoints for Warehouse Simulation Control
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from ..simulation.coordinator import Coordinator
from ..simulation.order import OrderManager

router = APIRouter(prefix="/api")

# We provide a dependency / singleton coordinator holder
_coordinator_instance: Coordinator = None

def get_coordinator() -> Coordinator:
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = Coordinator()
    return _coordinator_instance

class SpeedRequest(BaseModel):
    speed: float

@router.get("/state")
def get_simulation_state():
    coord = get_coordinator()
    return coord.get_state()

@router.get("/scenarios")
def list_scenarios():
    return OrderManager.get_scenario_definitions()

@router.post("/scenarios/{scenario_id}")
def load_scenario_endpoint(scenario_id: str):
    coord = get_coordinator()
    scenarios = OrderManager.get_scenario_definitions()
    if scenario_id not in scenarios:
        raise HTTPException(status_code=404, detail="Scenario not found")
    coord.load_scenario(scenario_id)
    return {"message": f"Loaded scenario {scenario_id}", "state": coord.get_state()}

@router.post("/control/start")
def start_simulation():
    coord = get_coordinator()
    coord.is_running = True
    return {"status": "started"}

@router.post("/control/pause")
def pause_simulation():
    coord = get_coordinator()
    coord.is_running = False
    return {"status": "paused"}

@router.post("/control/step")
def step_simulation():
    coord = get_coordinator()
    coord.is_running = False
    coord.step()
    return {"status": "stepped", "state": coord.get_state()}

@router.post("/control/reset")
def reset_simulation():
    coord = get_coordinator()
    coord.load_scenario(coord.current_scenario_id)
    return {"status": "reset", "state": coord.get_state()}

@router.post("/control/speed")
def set_simulation_speed(req: SpeedRequest):
    coord = get_coordinator()
    coord.speed_multiplier = max(0.2, min(5.0, req.speed))
    return {"status": "speed_updated", "speed": coord.speed_multiplier}

@router.get("/algorithms")
def get_algorithm_details():
    coord = get_coordinator()
    return {
        "status": coord.algorithm_status,
        "metrics": coord.metrics.to_dict(),
        "astar_samples": coord.last_astar_visual_data,
        "dp_samples": coord.last_dp_visual_data
    }
