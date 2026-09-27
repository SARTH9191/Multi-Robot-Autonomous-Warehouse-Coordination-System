"""
DAA Algorithms Package
Manually implemented algorithms for multi-robot warehouse coordination:
- BFS: Reachability, shortest path, and distance matrix
- DFS: Cycle detection for wait-for graphs and connected components
- A*: Time-space & 2D obstacle-avoiding heuristic pathfinding
- DP-TSP: Exact Held-Karp bitmask DP for warehouse item pickup sequence
- Geometry: Orientation, segment intersection, and continuous proximity
- Collision: Vertex, edge, intersection, and proximity hazard detection
- Scheduler: Greedy priority arbitration and dynamic replanning
"""
from .bfs import bfs_shortest_path, bfs_distance_matrix
from .dfs import detect_cycles_directed, dfs_connected_components
from .astar import astar_search
from .tsp_dp import solve_tsp_dp
from .geometry import orientation, segments_intersect, check_proximity, euclidean_distance, manhattan_distance, intersection_point
from .collision import (
    detect_vertex_conflicts,
    detect_edge_conflicts,
    detect_intersection_conflicts,
    detect_geometric_path_intersections,
    detect_live_proximities,
    ConflictType
)
from .scheduler import GreedyIntersectionScheduler, calculate_priority, SchedulerAction

__all__ = [
    "bfs_shortest_path",
    "bfs_distance_matrix",
    "detect_cycles_directed",
    "dfs_connected_components",
    "astar_search",
    "solve_tsp_dp",
    "orientation",
    "segments_intersect",
    "check_proximity",
    "euclidean_distance",
    "manhattan_distance",
    "intersection_point",
    "detect_vertex_conflicts",
    "detect_edge_conflicts",
    "detect_intersection_conflicts",
    "detect_geometric_path_intersections",
    "detect_live_proximities",
    "ConflictType",
    "GreedyIntersectionScheduler",
    "calculate_priority",
    "SchedulerAction"
]
