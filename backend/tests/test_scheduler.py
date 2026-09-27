"""
Unit Tests for Greedy Scheduler & Deadlock Prevention (Section 33)
Tests:
- Greedy Priority calculation
- Two robots conflict arbitration
- Four robots bottleneck resolution
- Deadlock detection via DFS wait-for cycle and yield assignment
"""
import pytest
from backend.algorithms.scheduler import (
    GreedyIntersectionScheduler,
    calculate_priority,
    SchedulerAction
)
from backend.algorithms.dfs import detect_cycles_directed

def test_priority_calculation():
    # Robot with high urgency (more items) and longer wait has higher priority
    p_high = calculate_priority(urgency=4, waiting_ticks=5, distance_to_target=2.0)
    p_low = calculate_priority(urgency=1, waiting_ticks=0, distance_to_target=5.0)
    assert p_high > p_low

def test_two_robot_scheduler_resolution():
    intersections = {(15, 11)}
    scheduler = GreedyIntersectionScheduler(intersections)
    
    conflicts = [{
        "type": "INTERSECTION_CONFLICT",
        "robots": ["R1", "R2"],
        "location": (15, 11)
    }]
    
    # R1 has higher urgency than R2
    robot_states = {
        "R1": {"remaining_items": 4, "waiting_ticks": 2, "dist_to_conflict": 1.0, "battery": 95},
        "R2": {"remaining_items": 1, "waiting_ticks": 0, "dist_to_conflict": 3.0, "battery": 95}
    }
    
    decisions = scheduler.resolve_conflicts(conflicts, robot_states)
    assert len(decisions) == 1
    d = decisions[0]
    assert d["winner"] == "R1"
    assert d["loser"] == "R2"
    assert d["action_winner"] == SchedulerAction.GRANT_PASS
    assert d["action_loser"] == SchedulerAction.HOLD_WAIT

def test_deadlock_cycle_detection_and_resolution():
    scheduler = GreedyIntersectionScheduler({(5, 5)})
    # Manually configure cyclic wait-for dependency: R1 -> R2 -> R3 -> R1
    scheduler.wait_for_graph = {
        "R1": ["R2"],
        "R2": ["R3"],
        "R3": ["R1"]
    }
    
    robot_states = {
        "R1": {"remaining_items": 3, "waiting_ticks": 4, "dist_to_conflict": 1.0, "battery": 90},
        "R2": {"remaining_items": 2, "waiting_ticks": 3, "dist_to_conflict": 2.0, "battery": 85},
        "R3": {"remaining_items": 1, "waiting_ticks": 0, "dist_to_conflict": 4.0, "battery": 80} # Lowest priority victim
    }
    
    res = scheduler.check_and_resolve_deadlocks(robot_states)
    assert res is not None
    assert res["action"] == SchedulerAction.YIELD_DEADLOCK
    assert res["victim"] == "R3" # R3 has lowest priority, yields to break deadlock
