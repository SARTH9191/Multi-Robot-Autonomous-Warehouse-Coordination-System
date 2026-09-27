"""
Unit Tests for A* Pathfinding Algorithm (Section 33)
Tests:
- Valid path finding on grid
- No path (completely surrounded by obstacles)
- Static obstacles avoidance
- Dynamic obstacles avoidance & spacetime reservation
"""
import pytest
from backend.algorithms.astar import astar_search

def test_astar_valid_path():
    start = (1, 1)
    goal = (5, 5)
    width, height = 10, 10
    obstacles = set()
    
    res = astar_search(start, goal, width, height, obstacles)
    assert res["found"] is True
    assert res["path"][0] == start
    assert res["path"][-1] == goal
    # Manhattan distance from (1,1) to (5,5) is 4 + 4 = 8 steps
    assert res["path_length"] == 8
    assert res["nodes_explored"] >= 8

def test_astar_no_path():
    start = (1, 1)
    goal = (5, 5)
    width, height = 10, 10
    # Completely box in start node with obstacles
    obstacles = {(0, 1), (2, 1), (1, 0), (1, 2)}
    
    res = astar_search(start, goal, width, height, obstacles)
    assert res["found"] is False
    assert len(res["path"]) == 0
    assert res["cost"] == float("inf")

def test_astar_static_obstacles():
    start = (1, 3)
    goal = (5, 3)
    width, height = 10, 10
    # Wall in between at x = 3 from y=1 to y=4
    obstacles = {(3, 1), (3, 2), (3, 3), (3, 4)}
    
    res = astar_search(start, goal, width, height, obstacles)
    assert res["found"] is True
    assert res["path"][0] == start
    assert res["path"][-1] == goal
    # Path must detour around wall, so no cell in obstacles is visited
    for node in res["path"]:
        assert node not in obstacles

def test_astar_dynamic_obstacles_and_reservation():
    start = (1, 1)
    goal = (3, 1)
    width, height = 10, 10
    static_obs = set()
    # Dynamic obstacle at (2, 1)
    dynamic_obs = {(2, 1)}
    
    res = astar_search(start, goal, width, height, static_obs, dynamic_obstacles=dynamic_obs)
    assert res["found"] is True
    assert (2, 1) not in res["path"]
    assert res["path"][0] == start
    assert res["path"][-1] == goal
