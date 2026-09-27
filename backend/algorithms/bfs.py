"""
Breadth-First Search (BFS) Module
Used for graph reachability, shortest hop distance, exploration wavefront visualization,
and all-pairs distance matrix computation for TSP.
"""
from collections import deque
from typing import List, Tuple, Set, Dict, Optional
import time

GridCoord = Tuple[int, int]

def bfs_shortest_path(
    start: GridCoord,
    goal: GridCoord,
    width: int,
    height: int,
    obstacles: Set[GridCoord],
    allow_diagonal: bool = False
) -> Dict:
    """
    Standard BFS for unweighted shortest path on grid graph.
    Returns path, nodes explored, and exploration history for visualization.
    """
    start_time = time.perf_counter()
    
    if start == goal:
        return {
            "found": True,
            "path": [start],
            "cost": 0,
            "nodes_explored": 1,
            "exploration_order": [start],
            "execution_time_ms": 0.0
        }
    
    queue = deque([start])
    visited: Set[GridCoord] = {start}
    parent: Dict[GridCoord, GridCoord] = {}
    exploration_order: List[GridCoord] = []
    
    # 4-connected grid neighbors
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    if allow_diagonal:
        directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
    found = False
    while queue:
        curr = queue.popleft()
        exploration_order.append(curr)
        
        if curr == goal:
            found = True
            break
            
        for dx, dy in directions:
            nx, ny = curr[0] + dx, curr[1] + dy
            neighbor = (nx, ny)
            
            if 0 <= nx < width and 0 <= ny < height:
                if neighbor not in obstacles and neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = curr
                    queue.append(neighbor)
                    
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    
    if not found:
        return {
            "found": False,
            "path": [],
            "cost": float("inf"),
            "nodes_explored": len(visited),
            "exploration_order": exploration_order,
            "execution_time_ms": round(elapsed_ms, 3)
        }
        
    # Reconstruct path from goal back to start
    path = []
    curr = goal
    while curr != start:
        path.append(curr)
        curr = parent[curr]
    path.append(start)
    path.reverse()
    
    return {
        "found": True,
        "path": path,
        "cost": len(path) - 1,
        "nodes_explored": len(visited),
        "exploration_order": exploration_order,
        "execution_time_ms": round(elapsed_ms, 3)
    }

def bfs_distance_matrix(
    locations: List[GridCoord],
    width: int,
    height: int,
    obstacles: Set[GridCoord]
) -> List[List[int]]:
    """
    Computes an n x n shortest distance matrix between all given points of interest.
    Useful for feeding into DP-TSP.
    """
    n = len(locations)
    dist_matrix = [[0] * n for _ in range(n)]
    
    for i in range(n):
        src = locations[i]
        # Run multi-target BFS from src
        queue = deque([(src, 0)])
        visited = {src: 0}
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        while queue:
            curr, d = queue.popleft()
            for dx, dy in directions:
                nx, ny = curr[0] + dx, curr[1] + dy
                neighbor = (nx, ny)
                if 0 <= nx < width and 0 <= ny < height:
                    if neighbor not in obstacles and neighbor not in visited:
                        visited[neighbor] = d + 1
                        queue.append((neighbor, d + 1))
                        
        for j in range(n):
            dst = locations[j]
            dist_matrix[i][j] = visited.get(dst, 999999)
            
    return dist_matrix
