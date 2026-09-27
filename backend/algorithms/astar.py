"""
A* Pathfinding Algorithm Module
Implements f(n) = g(n) + h(n) with Manhattan distance heuristic.
Supports static obstacles, dynamic obstacles, time-space reservations,
and returns full exploration wavefront for algorithm visualization.
"""
import heapq
import time
from typing import List, Tuple, Set, Dict, Optional, Any

GridCoord = Tuple[int, int]
SpaceTimeCoord = Tuple[int, int, int] # (x, y, t)

def manhattan(a: GridCoord, b: GridCoord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar_search(
    start: GridCoord,
    goal: GridCoord,
    width: int,
    height: int,
    static_obstacles: Set[GridCoord],
    dynamic_obstacles: Optional[Set[GridCoord]] = None,
    reservations: Optional[Set[Tuple[int, int, int]]] = None, # (x, y, t)
    start_time_tick: int = 0,
    allow_wait: bool = True,
    max_time_steps: int = 200
) -> Dict[str, Any]:
    """
    Finds shortest collision-safe path using A* search.
    If reservations are provided, plans in space-time (x, y, t).
    Otherwise plans in 2D space avoiding static and dynamic obstacles.
    """
    start_bench = time.perf_counter()
    dynamic_obstacles = dynamic_obstacles or set()
    reservations = reservations or set()
    
    if start == goal:
        return {
            "found": True,
            "path": [start],
            "timed_path": [(start[0], start[1], start_time_tick)],
            "path_length": 0,
            "cost": 0,
            "nodes_explored": 1,
            "open_nodes": [],
            "closed_nodes": [start],
            "execution_time_ms": 0.0
        }
        
    use_spacetime = len(reservations) > 0 or allow_wait
    
    # Priority Queue holds: (f_score, h_score, g_score, state, path)
    # state is (x, y, t) if spacetime else (x, y)
    initial_h = manhattan(start, goal)
    initial_state = (start[0], start[1], start_time_tick) if use_spacetime else start
    
    pq = []
    # tie-breaker counter
    counter = 0
    heapq.heappush(pq, (initial_h, 0, counter, initial_state))
    
    # Cost dictionary g_score
    g_score: Dict[Any, int] = {initial_state: 0}
    parent: Dict[Any, Any] = {}
    
    closed_nodes_list: List[GridCoord] = []
    closed_set: Set[Any] = set()
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    found_goal_state = None
    
    while pq:
        f, g, _, curr_state = heapq.heappop(pq)
        
        if curr_state in closed_set:
            continue
            
        closed_set.add(curr_state)
        curr_xy = (curr_state[0], curr_state[1])
        if curr_xy not in closed_nodes_list:
            closed_nodes_list.append(curr_xy)
            
        # Goal check
        if curr_xy == goal:
            found_goal_state = curr_state
            break
            
        t = curr_state[2] if use_spacetime else 0
        if use_spacetime and t >= start_time_tick + max_time_steps:
            continue
            
        # Possible actions: Move 4-directions + optionally Wait in place
        possible_moves = list(directions)
        if use_spacetime and allow_wait:
            possible_moves.append((0, 0)) # Wait in current cell
            
        for dx, dy in possible_moves:
            nx, ny = curr_xy[0] + dx, curr_xy[1] + dy
            next_t = t + 1 if use_spacetime else 0
            
            # Boundary check
            if not (0 <= nx < width and 0 <= ny < height):
                continue
                
            neighbor_xy = (nx, ny)
            
            # Static obstacle check
            if neighbor_xy in static_obstacles and neighbor_xy != goal:
                continue
                
            # Dynamic obstacle check (other stationary robots or blocked cell)
            if neighbor_xy in dynamic_obstacles and neighbor_xy != goal:
                continue
                
            if use_spacetime:
                # Vertex collision in reservation table
                if (nx, ny, next_t) in reservations:
                    continue
                # Edge / swap collision: check if someone was at (nx, ny, t) moving to (curr_x, curr_y, next_t)
                if (curr_xy[0], curr_xy[1], next_t) in reservations and (nx, ny, t) in reservations:
                    continue
                next_state = (nx, ny, next_t)
            else:
                next_state = neighbor_xy
                
            # Cost: waiting has a slight penalty (1.1) to encourage active movement
            step_cost = 1 if (dx != 0 or dy != 0) else 1
            tentative_g = g + step_cost
            
            if next_state not in g_score or tentative_g < g_score[next_state]:
                g_score[next_state] = tentative_g
                h = manhattan(neighbor_xy, goal)
                f_score = tentative_g + h
                counter += 1
                parent[next_state] = curr_state
                heapq.heappush(pq, (f_score, tentative_g, counter, next_state))
                
    elapsed_ms = (time.perf_counter() - start_bench) * 1000.0
    
    # Collect open nodes for visualizer
    open_nodes_list = []
    seen_open = set()
    for item in pq:
        st = item[3]
        xy = (st[0], st[1])
        if xy not in seen_open and xy not in closed_nodes_list:
            seen_open.add(xy)
            open_nodes_list.append(xy)
            
    if found_goal_state is None:
        return {
            "found": False,
            "path": [],
            "timed_path": [],
            "path_length": 0,
            "cost": float("inf"),
            "nodes_explored": len(closed_nodes_list),
            "open_nodes": open_nodes_list,
            "closed_nodes": closed_nodes_list,
            "execution_time_ms": round(elapsed_ms, 3)
        }
        
    # Reconstruct path
    reconstructed_path: List[GridCoord] = []
    timed_path: List[Tuple[int, int, int]] = []
    curr = found_goal_state
    
    while curr in parent:
        reconstructed_path.append((curr[0], curr[1]))
        if use_spacetime:
            timed_path.append(curr)
        curr = parent[curr]
    reconstructed_path.append((curr[0], curr[1]))
    if use_spacetime:
        timed_path.append(curr)
        
    reconstructed_path.reverse()
    timed_path.reverse()
    
    return {
        "found": True,
        "path": reconstructed_path,
        "timed_path": timed_path,
        "path_length": len(reconstructed_path) - 1,
        "cost": g_score[found_goal_state],
        "nodes_explored": len(closed_nodes_list),
        "open_nodes": open_nodes_list,
        "closed_nodes": closed_nodes_list,
        "execution_time_ms": round(elapsed_ms, 3)
    }
