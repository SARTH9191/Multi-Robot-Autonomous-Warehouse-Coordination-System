"""
Greedy Conflict-Free Aisle & Intersection Scheduler
Implements:
- Priority calculation: priority = urgency + waitingTime - distanceFactor
- Reservation management for shared narrow aisles and intersections
- Dynamic replanning triggers
- Deadlock detection & resolution via DFS wait-for cycle analysis
"""
from typing import Dict, List, Set, Tuple, Optional, Any
from .dfs import detect_cycles_directed
from .astar import astar_search

Point = Tuple[int, int]

class SchedulerAction:
    GRANT_PASS = "GRANT_PASS"
    HOLD_WAIT = "HOLD_WAIT"
    TRIGGER_REPLAN = "TRIGGER_REPLAN"
    YIELD_DEADLOCK = "YIELD_DEADLOCK"

def calculate_priority(
    urgency: float,
    waiting_ticks: int,
    distance_to_target: float,
    battery_level: float = 100.0
) -> float:
    """
    Greedy priority formula:
    priority = (urgency * 10.0) + (waiting_ticks * 2.5) - (distance_to_target * 0.8) + (100 - battery_level) * 0.1
    
    Explanation:
    - Urgency: High priority / remaining items count weight.
    - Waiting time: Ensures fairness and prevents starvation.
    - Distance factor: Closer robot to bottleneck gets precedence to clear it faster.
    """
    distance_factor = distance_to_target * 0.8
    wait_factor = waiting_ticks * 2.5
    urgency_factor = urgency * 10.0
    battery_factor = (100.0 - battery_level) * 0.05
    return urgency_factor + wait_factor - distance_factor + battery_factor

class GreedyIntersectionScheduler:
    def __init__(self, intersections: Set[Point]):
        self.intersections = intersections
        # Map: intersection_point -> active_occupant_robot_id
        self.active_reservations: Dict[Point, str] = {}
        # Map: intersection_point -> list of waiting robot_ids
        self.wait_queues: Dict[Point, List[str]] = {pt: [] for pt in intersections}
        # Deadlock wait-for graph: robot_a -> [robot_b, ...]
        self.wait_for_graph: Dict[str, List[str]] = {}

    def resolve_conflicts(
        self,
        conflicts: List[Dict[str, Any]],
        robot_states: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Processes conflicts and determines arbitration actions for each conflicting robot.
        Returns a list of schedule decisions.
        """
        decisions = []
        handled_pairs = set()

        for conf in conflicts:
            c_type = conf.get("type")
            robots = conf.get("robots", [])
            if len(robots) < 2:
                continue

            r1, r2 = robots[0], robots[1]
            pair_key = tuple(sorted([r1, r2]))
            if pair_key in handled_pairs:
                continue
            handled_pairs.add(pair_key)

            st1 = robot_states.get(r1, {})
            st2 = robot_states.get(r2, {})

            p1 = calculate_priority(
                urgency=st1.get("remaining_items", 1),
                waiting_ticks=st1.get("waiting_ticks", 0),
                distance_to_target=st1.get("dist_to_conflict", 5.0),
                battery_level=st1.get("battery", 100.0)
            )
            p2 = calculate_priority(
                urgency=st2.get("remaining_items", 1),
                waiting_ticks=st2.get("waiting_ticks", 0),
                distance_to_target=st2.get("dist_to_conflict", 5.0),
                battery_level=st2.get("battery", 100.0)
            )

            # Robot with higher priority wins
            if p1 >= p2:
                winner, loser = r1, r2
                winner_p, loser_p = p1, p2
            else:
                winner, loser = r2, r1
                winner_p, loser_p = p2, p1

            # Check conflict severity
            is_head_on = (c_type == "EDGE_CONFLICT")
            
            # Register wait dependency for cycle detection
            if loser not in self.wait_for_graph:
                self.wait_for_graph[loser] = []
            if winner not in self.wait_for_graph[loser]:
                self.wait_for_graph[loser].append(winner)

            decisions.append({
                "conflict_type": c_type,
                "winner": winner,
                "winner_priority": round(winner_p, 2),
                "loser": loser,
                "loser_priority": round(loser_p, 2),
                "action_winner": SchedulerAction.GRANT_PASS,
                "action_loser": SchedulerAction.TRIGGER_REPLAN if is_head_on else SchedulerAction.HOLD_WAIT,
                "location": conf.get("location") or conf.get("edge"),
                "reason": f"Greedy priority: {winner} ({round(winner_p,1)}) > {loser} ({round(loser_p,1)})"
            })

        return decisions

    def check_and_resolve_deadlocks(
        self,
        robot_states: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Builds directed wait-for graph and runs DFS to check for cyclic dependencies.
        If cycle found, selects the robot with lowest priority to yield and reroute.
        """
        has_cycle, cycle = detect_cycles_directed(self.wait_for_graph)
        if not has_cycle or not cycle:
            return None

        # Cycle found, e.g. ['R1', 'R2', 'R3', 'R1']
        cycle_unique = list(dict.fromkeys(cycle))
        
        # Pick victim with lowest priority to yield
        lowest_priority = float("inf")
        victim = cycle_unique[0]

        for r_id in cycle_unique:
            st = robot_states.get(r_id, {})
            p = calculate_priority(
                urgency=st.get("remaining_items", 1),
                waiting_ticks=st.get("waiting_ticks", 0),
                distance_to_target=st.get("dist_to_conflict", 5.0),
                battery_level=st.get("battery", 100.0)
            )
            if p < lowest_priority:
                lowest_priority = p
                victim = r_id

        # Clear victim's outgoing dependencies
        if victim in self.wait_for_graph:
            self.wait_for_graph[victim] = []

        return {
            "cycle": cycle,
            "victim": victim,
            "action": SchedulerAction.YIELD_DEADLOCK,
            "description": f"Deadlock cycle detected: {' -> '.join(cycle)}. Robot {victim} ordered to yield and reroute."
        }

    def clear_dependencies(self, robot_id: str):
        """Remove robot from wait-for graph once it completes move or replans."""
        if robot_id in self.wait_for_graph:
            self.wait_for_graph[robot_id] = []
        for r, deps in self.wait_for_graph.items():
            if robot_id in deps:
                deps.remove(robot_id)
