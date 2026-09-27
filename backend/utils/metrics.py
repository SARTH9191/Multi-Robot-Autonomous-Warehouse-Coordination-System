"""
Simulation & Algorithm Performance Metrics
Aggregates live statistics for Section 17, 23, and 36.
"""
from typing import Dict, Any, List

class PerformanceMetrics:
    def __init__(self):
        self.simulation_ticks = 0
        self.total_distance_meters = 0.0
        self.total_waiting_seconds = 0.0
        
        # Conflict & Safety counters
        self.conflicts_detected = 0
        self.conflicts_resolved = 0
        self.path_replans = 0
        self.collisions_count = 0  # Goal: strictly 0
        self.deadlocks_detected = 0
        self.deadlocks_resolved = 0
        
        # Order fulfillment counters
        self.total_items_to_pick = 0
        self.items_picked_count = 0
        self.orders_completed_count = 0
        
        # Algorithm benchmarks
        self.astar_total_nodes = 0
        self.astar_runs = 0
        self.astar_total_time_ms = 0.0
        
        self.dp_states_total = 0
        self.dp_runs = 0
        self.dp_total_time_ms = 0.0

    def record_astar_run(self, nodes_explored: int, time_ms: float):
        self.astar_runs += 1
        self.astar_total_nodes += nodes_explored
        self.astar_total_time_ms += time_ms

    def record_dp_run(self, states_computed: int, time_ms: float):
        self.dp_runs += 1
        self.dp_states_total += states_computed
        self.dp_total_time_ms += time_ms

    def to_dict(self) -> Dict[str, Any]:
        avg_astar_time = (
            round(self.astar_total_time_ms / self.astar_runs, 2)
            if self.astar_runs > 0 else 0.0
        )
        avg_dp_time = (
            round(self.dp_total_time_ms / self.dp_runs, 2)
            if self.dp_runs > 0 else 0.0
        )
        
        return {
            "simulation_ticks": self.simulation_ticks,
            "total_distance_m": round(self.total_distance_meters, 1),
            "total_waiting_sec": round(self.total_waiting_seconds, 1),
            "conflicts_detected": self.conflicts_detected,
            "conflicts_resolved": self.conflicts_resolved,
            "path_replans": self.path_replans,
            "collisions": self.collisions_count,
            "deadlocks_detected": self.deadlocks_detected,
            "deadlocks_resolved": self.deadlocks_resolved,
            "total_items": self.total_items_to_pick,
            "items_picked": self.items_picked_count,
            "orders_completed": self.orders_completed_count,
            "astar_runs": self.astar_runs,
            "astar_total_nodes": self.astar_nodes_explored if hasattr(self, 'astar_nodes_explored') else self.astar_total_nodes,
            "avg_planning_time_ms": avg_astar_time,
            "dp_states_total": self.dp_states_total,
            "avg_dp_time_ms": avg_dp_time
        }

    def reset(self):
        self.__init__()
