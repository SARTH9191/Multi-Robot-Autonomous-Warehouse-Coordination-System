"""
Collision Detection & Conflict Analysis Module
Implements:
1. Vertex Conflicts (Two robots occupying the same cell at timestep t)
2. Edge Conflicts (Robots swapping adjacent cells at t -> t+1)
3. Intersection Conflicts (Approaching shared intersection nodes within lookahead horizon)
4. Continuous Proximity Checks & Line Segment Path Crossing (Computational Geometry)
"""
from typing import List, Dict, Tuple, Set, Optional, Any
from .geometry import segments_intersect, intersection_point, check_proximity, euclidean_distance

Point = Tuple[int, int]
FloatPoint = Tuple[float, float]

class ConflictType:
    VERTEX = "VERTEX_CONFLICT"
    EDGE = "EDGE_CONFLICT"
    INTERSECTION = "INTERSECTION_CONFLICT"
    PROXIMITY = "PROXIMITY_WARNING"

def detect_vertex_conflicts(
    robot_trajectories: Dict[str, List[Point]],
    horizon: int = 15
) -> List[Dict[str, Any]]:
    """
    Check if two robots are planned to occupy the same grid cell at the same time step.
    robot_trajectories: {robot_id: [(x0, y0), (x1, y1), ...]}
    """
    conflicts = []
    robot_ids = list(robot_trajectories.keys())
    
    for t in range(horizon):
        occupants: Dict[Point, str] = {}
        for r_id in robot_ids:
            path = robot_trajectories[r_id]
            if not path:
                continue
            # If t exceeds current path, the robot stays at its terminal position
            pos = path[t] if t < len(path) else path[-1]
            if pos in occupants:
                conflicts.append({
                    "type": ConflictType.VERTEX,
                    "time_step": t,
                    "robots": [occupants[pos], r_id],
                    "location": pos,
                    "description": f"Vertex conflict at {pos} at timestep t={t} between {occupants[pos]} and {r_id}"
                })
            else:
                occupants[pos] = r_id
                
    return conflicts

def detect_edge_conflicts(
    robot_trajectories: Dict[str, List[Point]],
    horizon: int = 15
) -> List[Dict[str, Any]]:
    """
    Check if two robots swap adjacent cells between timestep t and t+1.
    e.g., R1 moves A -> B while R2 moves B -> A.
    """
    conflicts = []
    robot_ids = list(robot_trajectories.keys())
    
    for i in range(len(robot_ids)):
        r1 = robot_ids[i]
        path1 = robot_trajectories[r1]
        for j in range(i + 1, len(robot_ids)):
            r2 = robot_ids[j]
            path2 = robot_trajectories[r2]
            
            max_t = min(horizon - 1, max(len(path1), len(path2)) - 1)
            for t in range(max_t):
                p1_curr = path1[t] if t < len(path1) else path1[-1]
                p1_next = path1[t + 1] if t + 1 < len(path1) else path1[-1]
                p2_curr = path2[t] if t < len(path2) else path2[-1]
                p2_next = path2[t + 1] if t + 1 < len(path2) else path2[-1]
                
                # Check head-on swap
                if p1_curr == p2_next and p1_next == p2_curr and p1_curr != p1_next:
                    conflicts.append({
                        "type": ConflictType.EDGE,
                        "time_step": t,
                        "robots": [r1, r2],
                        "edge": (p1_curr, p1_next),
                        "description": f"Head-on edge swap conflict between {r1} and {r2} on edge {p1_curr} <-> {p1_next}"
                    })
                    
    return conflicts

def detect_intersection_conflicts(
    robot_trajectories: Dict[str, List[Point]],
    intersections: Set[Point],
    time_window: int = 3,
    horizon: int = 20
) -> List[Dict[str, Any]]:
    """
    Check if multiple robots enter the same intersection within a close time window.
    """
    conflicts = []
    robot_ids = list(robot_trajectories.keys())
    
    for inter in intersections:
        # Collect arrival times for each robot at this intersection
        arrivals: Dict[str, List[int]] = {}
        for r_id in robot_ids:
            path = robot_trajectories[r_id]
            for t, pos in enumerate(path[:horizon]):
                if pos == inter:
                    if r_id not in arrivals:
                        arrivals[r_id] = []
                    arrivals[r_id].append(t)
                    
        # Check pairs of robots arriving within time_window
        arrived_robots = list(arrivals.keys())
        for i in range(len(arrived_robots)):
            r1 = arrived_robots[i]
            for j in range(i + 1, len(arrived_robots)):
                r2 = arrived_robots[j]
                min_t1 = min(arrivals[r1])
                min_t2 = min(arrivals[r2])
                if abs(min_t1 - min_t2) <= time_window:
                    conflicts.append({
                        "type": ConflictType.INTERSECTION,
                        "time_step": min(min_t1, min_t2),
                        "robots": [r1, r2],
                        "location": inter,
                        "t_diff": abs(min_t1 - min_t2),
                        "description": f"Intersection collision hazard at {inter} between {r1} (t={min_t1}) and {r2} (t={min_t2})"
                    })
                    
    return conflicts

def detect_geometric_path_intersections(
    robot_trajectories: Dict[str, List[Point]],
    lookahead_steps: int = 8
) -> List[Dict[str, Any]]:
    """
    Computes geometric line segment intersections between current motion vectors.
    Uses orientation and segments_intersect from computational geometry.
    """
    conflicts = []
    robot_ids = list(robot_trajectories.keys())
    
    for i in range(len(robot_ids)):
        r1 = robot_ids[i]
        path1 = robot_trajectories[r1][:lookahead_steps]
        for j in range(i + 1, len(robot_ids)):
            r2 = robot_ids[j]
            path2 = robot_trajectories[r2][:lookahead_steps]
            
            # Compare segments
            for s1 in range(len(path1) - 1):
                p1a, p1b = path1[s1], path1[s1 + 1]
                for s2 in range(len(path2) - 1):
                    p2a, p2b = path2[s2], path2[s2 + 1]
                    
                    if segments_intersect(p1a, p1b, p2a, p2b):
                        pt = intersection_point(p1a, p1b, p2a, p2b)
                        # Filter out non-problematic touches if time is separated
                        conflicts.append({
                            "type": "GEOMETRIC_CROSSING",
                            "robots": [r1, r2],
                            "segment_1": (p1a, p1b),
                            "segment_2": (p2a, p2b),
                            "crossing_point": pt,
                            "step_indices": (s1, s2)
                        })
    return conflicts

def detect_live_proximities(
    robot_positions: Dict[str, FloatPoint],
    safety_radius: float = 1.25
) -> List[Dict[str, Any]]:
    """
    Real-time continuous safety distance monitor.
    """
    warnings = []
    robot_ids = list(robot_positions.keys())
    for i in range(len(robot_ids)):
        r1 = robot_ids[i]
        for j in range(i + 1, len(robot_ids)):
            r2 = robot_ids[j]
            is_close, dist = check_proximity(robot_positions[r1], robot_positions[r2], safety_radius)
            if is_close:
                warnings.append({
                    "type": ConflictType.PROXIMITY,
                    "robots": [r1, r2],
                    "distance": round(dist, 2),
                    "safety_radius": safety_radius,
                    "description": f"Proximity warning: {r1} and {r2} within {round(dist, 2)}m (< {safety_radius}m)"
                })
    return warnings
