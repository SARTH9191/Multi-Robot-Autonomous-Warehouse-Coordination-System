"""
Unit Tests for Collision & Computational Geometry (Section 33)
Tests:
- Vertex Conflict (Same cell occupied at timestep t)
- Edge Conflict (Robots swapping adjacent cells)
- Intersection Conflict (Robots entering same intersection node)
- Proximity & Safe distance detection
"""
import pytest
from backend.algorithms.collision import (
    detect_vertex_conflicts,
    detect_edge_conflicts,
    detect_intersection_conflicts,
    detect_live_proximities,
    ConflictType
)
from backend.algorithms.geometry import segments_intersect, orientation

def test_vertex_conflict_detection():
    # R1 and R2 both reach (5, 5) at timestep t=2
    trajectories = {
        "R1": [(3, 5), (4, 5), (5, 5), (6, 5)],
        "R2": [(5, 3), (5, 4), (5, 5), (5, 6)]
    }
    conflicts = detect_vertex_conflicts(trajectories, horizon=5)
    assert len(conflicts) >= 1
    c = conflicts[0]
    assert c["type"] == ConflictType.VERTEX
    assert c["time_step"] == 2
    assert c["location"] == (5, 5)
    assert set(c["robots"]) == {"R1", "R2"}

def test_edge_swap_conflict_detection():
    # At t=1, R1 moves from (5,5) -> (5,6) while R2 moves from (5,6) -> (5,5)
    trajectories = {
        "R1": [(4, 5), (5, 5), (5, 6), (5, 7)],
        "R2": [(6, 6), (5, 6), (5, 5), (4, 5)]
    }
    conflicts = detect_edge_conflicts(trajectories, horizon=5)
    assert len(conflicts) >= 1
    c = conflicts[0]
    assert c["type"] == ConflictType.EDGE
    assert c["time_step"] == 1
    assert set(c["robots"]) == {"R1", "R2"}

def test_intersection_conflict_detection():
    intersections = {(10, 10)}
    trajectories = {
        "R1": [(8, 10), (9, 10), (10, 10), (11, 10)], # Arrives at t=2
        "R2": [(10, 8), (10, 9), (10, 10), (10, 11)]  # Arrives at t=2
    }
    conflicts = detect_intersection_conflicts(trajectories, intersections, time_window=1, horizon=5)
    assert len(conflicts) >= 1
    assert conflicts[0]["type"] == ConflictType.INTERSECTION
    assert conflicts[0]["location"] == (10, 10)

def test_computational_geometry_segment_intersection():
    # Crossing segments: (0,0)-(2,2) and (0,2)-(2,0)
    assert segments_intersect((0, 0), (2, 2), (0, 2), (2, 0)) is True
    # Parallel non-intersecting segments
    assert segments_intersect((0, 0), (2, 0), (0, 2), (2, 2)) is False

def test_live_proximity_detection():
    # Position within safety radius of 1.2m
    positions = {
        "R1": (5.0, 5.0),
        "R2": (5.5, 5.2), # Distance = sqrt(0.5^2 + 0.2^2) = ~0.538m < 1.2m
        "R3": (10.0, 10.0)
    }
    warnings = detect_live_proximities(positions, safety_radius=1.2)
    assert len(warnings) == 1
    assert set(warnings[0]["robots"]) == {"R1", "R2"}
