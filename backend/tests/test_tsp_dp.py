"""
Unit Tests for DP-TSP Order Optimization Algorithm (Section 33)
Tests:
- 1 item base case
- 2 items order selection
- Multiple items optimal permutation
- Route reconstruction accuracy
"""
import pytest
from backend.algorithms.tsp_dp import solve_tsp_dp

def test_dp_tsp_single_item():
    start = (0, 0)
    shelves = [(5, 5)]
    packing = (10, 10)
    
    res = solve_tsp_dp(start, shelves, packing)
    assert res["is_exact_dp"] is True
    assert res["optimal_sequence"] == [0]
    # Distance: (0,0)->(5,5) = 10, (5,5)->(10,10) = 10 -> Total 20
    assert res["optimized_cost"] == 20

def test_dp_tsp_two_items():
    start = (0, 0)
    # Shelf 0 is at (10, 0), Shelf 1 is at (2, 0). Packing is at (12, 0)
    # Natural order: (0,0) -> (10,0) -> (2,0) -> (12,0) = 10 + 8 + 10 = 28
    # Optimal order: (0,0) -> (2,0) -> (10,0) -> (12,0) = 2 + 8 + 2 = 12
    shelves = [(10, 0), (2, 0)]
    packing = (12, 0)
    
    res = solve_tsp_dp(start, shelves, packing)
    assert res["is_exact_dp"] is True
    assert res["optimal_sequence"] == [1, 0] # Shelf 1 first, then Shelf 0
    assert res["optimized_cost"] == 12
    assert res["saved_distance"] == 16 # Saved 28 - 12 = 16!

def test_dp_tsp_multiple_items_reconstruction():
    start = (0, 0)
    shelves = [(1, 0), (5, 0), (3, 0), (8, 0)]
    packing = (10, 0)
    
    res = solve_tsp_dp(start, shelves, packing)
    assert res["is_exact_dp"] is True
    # The optimal path along a line is clearly in increasing coordinate order: (1,0) -> (3,0) -> (5,0) -> (8,0)
    # Indices: 0 (1,0), 2 (3,0), 1 (5,0), 3 (8,0)
    assert res["optimal_sequence"] == [0, 2, 1, 3]
    assert res["optimized_cost"] == 10 # straight line distance to 10
    assert len(res["optimal_positions"]) == len(shelves) + 2
