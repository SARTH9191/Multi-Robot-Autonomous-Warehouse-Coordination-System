"""
Depth-First Search (DFS) Module
Used for cycle detection in wait-for resource dependency graphs (deadlock detection),
connected components verification, and deep graph traversal.
"""
from typing import List, Dict, Set, Tuple, Optional
import time

def detect_cycles_directed(adj: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
    """
    Detects cycles in a directed resource/wait-for graph using 3-color DFS.
    State 0: Unvisited (White)
    State 1: Currently visiting / in recursion stack (Gray)
    State 2: Completely visited (Black)
    
    Returns (has_cycle, cycle_nodes)
    """
    color: Dict[str, int] = {node: 0 for node in adj}
    parent: Dict[str, Optional[str]] = {node: None for node in adj}
    cycle_nodes: List[str] = []
    
    def dfs_visit(node: str) -> bool:
        color[node] = 1 # Gray
        for neighbor in adj.get(node, []):
            if neighbor not in color:
                color[neighbor] = 0
                parent[neighbor] = None
                
            if color[neighbor] == 1:
                # Cycle detected! Reconstruct cycle
                curr = node
                cycle = [neighbor]
                while curr != neighbor and curr is not None:
                    cycle.append(curr)
                    curr = parent.get(curr)
                cycle.append(neighbor)
                cycle.reverse()
                cycle_nodes.extend(cycle)
                return True
            elif color[neighbor] == 0:
                parent[neighbor] = node
                if dfs_visit(neighbor):
                    return True
                    
        color[node] = 2 # Black
        return False

    for node in list(adj.keys()):
        if color[node] == 0:
            if dfs_visit(node):
                return True, cycle_nodes
                
    return False, []

def dfs_connected_components(nodes: Set[Tuple[int, int]], obstacles: Set[Tuple[int, int]], width: int, height: int) -> List[Set[Tuple[int, int]]]:
    """
    Find connected components of walkable floor cells using DFS.
    """
    visited: Set[Tuple[int, int]] = set()
    components: List[Set[Tuple[int, int]]] = []
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    for start_node in nodes:
        if start_node in visited or start_node in obstacles:
            continue
            
        stack = [start_node]
        visited.add(start_node)
        current_comp = {start_node}
        
        while stack:
            curr = stack.pop()
            for dx, dy in directions:
                nx, ny = curr[0] + dx, curr[1] + dy
                neighbor = (nx, ny)
                if 0 <= nx < width and 0 <= ny < height:
                    if neighbor not in obstacles and neighbor not in visited:
                        visited.add(neighbor)
                        current_comp.add(neighbor)
                        stack.append(neighbor)
                        
        components.append(current_comp)
        
    return components
