"""
Robot Model & Agent State Machine
Represents an Autonomous Guided Vehicle (AGV) operating in the warehouse.
Maintains continuous position, heading, battery, cargo, and movement transitions.
"""
from typing import List, Tuple, Dict, Optional, Any
import math

GridCoord = Tuple[int, int]

class RobotStatus:
    IDLE = "IDLE"
    MOVING = "MOVING"
    PICKING = "PICKING"
    WAITING = "WAITING"
    REPLANNING = "REPLANNING"
    DELIVERING = "DELIVERING"
    CHARGING = "CHARGING"
    COMPLETED = "COMPLETED"

class Robot:
    def __init__(
        self,
        robot_id: str,
        name: str,
        color: str,
        color_hex: str,
        initial_pos: GridCoord
    ):
        self.id = robot_id
        self.name = name
        self.color = color
        self.color_hex = color_hex
        
        # Grid coordinates
        self.grid_x = initial_pos[0]
        self.grid_y = initial_pos[1]
        
        # Continuous coordinates for smooth canvas interpolation
        self.x = float(initial_pos[0])
        self.y = float(initial_pos[1])
        
        # Heading angle in degrees (0 = East, 90 = South, 180 = West, 270 = North)
        self.heading = 0.0
        
        # Operational State
        self.status = RobotStatus.IDLE
        self.previous_status = RobotStatus.IDLE
        
        # Telemetry & Resource stats
        self.battery = 98.0
        self.distance_traveled = 0.0 # meters (1 cell = 1.5m)
        self.waiting_ticks = 0
        self.replanning_ticks = 0
        
        # Mission / Order state
        self.assigned_order: Optional[Dict[str, Any]] = None
        self.unvisited_shelves: List[str] = []
        self.current_target_id: Optional[str] = None
        self.current_target_pos: Optional[GridCoord] = None
        self.cargo: List[str] = []
        
        # Navigation
        self.planned_path: List[GridCoord] = []
        self.path_index = 0
        self.timed_path: List[Tuple[int, int, int]] = []
        
        # Action Timers
        self.action_progress = 0.0 # 0% to 100%
        self.action_duration_ticks = 15 # e.g. 15 ticks for picking/packing
        self.current_action_tick = 0
        
        # Algorithm Performance metrics
        self.astar_nodes_explored = 0
        self.replan_count = 0
        self.dp_order_info: Optional[Dict[str, Any]] = None

    def get_pos(self) -> GridCoord:
        return (self.grid_x, self.grid_y)

    def set_order(self, order: Dict[str, Any], optimized_sequence: List[str], dp_info: Dict[str, Any]):
        """Assigns an optimized order to this robot."""
        self.assigned_order = order
        self.unvisited_shelves = list(optimized_sequence)
        self.dp_order_info = dp_info
        self.status = RobotStatus.IDLE

    def update_heading_towards(self, target: GridCoord):
        """Calculates direction-aware heading angle towards target neighbor."""
        dx = target[0] - self.grid_x
        dy = target[1] - self.grid_y
        if dx == 1 and dy == 0:
            self.heading = 0.0    # East
        elif dx == -1 and dy == 0:
            self.heading = 180.0  # West
        elif dx == 0 and dy == 1:
            self.heading = 90.0   # South
        elif dx == 0 and dy == -1:
            self.heading = 270.0  # North

    def step_towards(self, target_pos: GridCoord, move_fraction: float = 0.35):
        """
        Smoothly interpolates continuous position (x, y) towards next grid target.
        """
        self.update_heading_towards(target_pos)
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 0.08:
            # Snap to grid cell
            self.grid_x = target_pos[0]
            self.grid_y = target_pos[1]
            self.x = float(self.grid_x)
            self.y = float(self.grid_y)
            return True # Reached target cell
        else:
            step = min(dist, move_fraction)
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
            self.distance_traveled += step * 1.5 # 1.5m per cell
            self.battery = max(5.0, self.battery - 0.005 * step)
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Serializes robot state for WebSocket transmission."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "color_hex": self.color_hex,
            "x": round(self.x, 3),
            "y": round(self.y, 3),
            "grid_x": self.grid_x,
            "grid_y": self.grid_y,
            "heading": round(self.heading, 1),
            "status": self.status,
            "battery": round(self.battery, 1),
            "distance": round(self.distance_traveled, 1),
            "waiting_ticks": self.waiting_ticks,
            "replans": self.replan_count,
            "current_target": self.current_target_id,
            "unvisited_count": len(self.unvisited_shelves),
            "cargo": list(self.cargo),
            "action_progress": round(self.action_progress, 1),
            "path": self.planned_path[self.path_index:],
            "astar_nodes": self.astar_nodes_explored,
            "dp_info": self.dp_order_info
        }
