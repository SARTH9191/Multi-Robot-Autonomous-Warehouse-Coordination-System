"""
Order Generation & Scenario Configuration Module
Creates realistic warehouse pick lists and coordinates scenario setup
with DP-TSP optimization on shelf sequences.
"""
from typing import Dict, List, Tuple, Any
from ..algorithms.tsp_dp import solve_tsp_dp
from .warehouse import Warehouse

Point = Tuple[int, int]

class OrderManager:
    @staticmethod
    def optimize_robot_order(
        robot_start: Point,
        shelf_ids: List[str],
        packing_station: Point,
        warehouse: Warehouse
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        Runs DP-TSP to find the optimal order to visit shelf locations.
        """
        # Map shelf IDs to pickup coordinates
        shelf_coords = []
        valid_shelves = []
        for s_id in shelf_ids:
            if s_id in warehouse.shelf_definitions:
                shelf_coords.append(warehouse.shelf_definitions[s_id]["pickup_cell"])
                valid_shelves.append(s_id)
                
        dp_result = solve_tsp_dp(
            start_pos=robot_start,
            shelf_positions=shelf_coords,
            packing_pos=packing_station
        )
        
        # Map optimal index sequence back to shelf IDs
        opt_seq_indices = dp_result["optimal_sequence"]
        optimized_shelf_ids = [valid_shelves[i] for i in opt_seq_indices]
        
        return optimized_shelf_ids, dp_result

    @staticmethod
    def get_scenario_definitions() -> Dict[str, Dict[str, Any]]:
        """
        Returns the 6 required university course demo scenarios.
        """
        return {
            "SCENARIO_1": {
                "id": "SCENARIO_1",
                "name": "Scenario 1 — Normal Operation",
                "badge": "Standard Flow",
                "description": "Standard multi-robot fulfillment across distinct warehouse quadrants with minimal intersection congestion.",
                "orders": {
                    "R1": ["F1", "F3", "A3"],
                    "R2": ["H2", "H4", "C2"],
                    "R3": ["A1", "A4", "D2"],
                    "R4": ["C1", "C4", "E3"]
                },
                "dynamic_obstacles": []
            },
            "SCENARIO_2": {
                "id": "SCENARIO_2",
                "name": "Scenario 2 — Intersection Conflict",
                "badge": "2-Robot Conflict",
                "description": "Robots R1 and R2 navigate cross-aisles to arrive at central intersection (15, 11) at the exact same timestep.",
                "orders": {
                    # R1 from bottom-left aims across center to Cluster C
                    "R1": ["B4", "C3"],
                    # R2 from bottom-right aims across center to Cluster A
                    "R2": ["B1", "A2"],
                    "R3": ["D4"],
                    "R4": ["E1"]
                },
                "dynamic_obstacles": []
            },
            "SCENARIO_3": {
                "id": "SCENARIO_3",
                "name": "Scenario 3 — Four Robot Conflict",
                "badge": "4-Way Convergence",
                "description": "All four robots converge simultaneously toward the central bottleneck highway (x=15-16, y=11-12), testing greedy priority arbitration and queuing.",
                "orders": {
                    "R1": ["E2", "C3"],
                    "R2": ["D1", "A3"],
                    "R3": ["H2", "F4"],
                    "R4": ["F1", "D3"]
                },
                "dynamic_obstacles": []
            },
            "SCENARIO_4": {
                "id": "SCENARIO_4",
                "name": "Scenario 4 — Dynamic Obstacle Reroute",
                "badge": "Dynamic Replanning",
                "description": "A simulated spill barrier blocks the primary northern corridor at (10, 6) and (15, 6). Robots must dynamically detect the blockage and replan via A*.",
                "orders": {
                    "R1": ["A3", "B2"],
                    "R2": ["C2", "B4"],
                    "R3": ["B3", "E1"],
                    "R4": ["D2", "F2"]
                },
                "dynamic_obstacles": [(10, 6), (15, 6)]
            },
            "SCENARIO_5": {
                "id": "SCENARIO_5",
                "name": "Scenario 5 — Deadlock Detection & Yield",
                "badge": "Deadlock Test",
                "description": "Robots head in opposite directions in a narrow 1-cell wide corridor, testing DFS wait-for cycle detection and automated priority yielding.",
                "orders": {
                    "R1": ["C2"],
                    "R4": ["F1"],
                    "R2": ["A1"],
                    "R3": ["H4"]
                },
                "dynamic_obstacles": [(15, 5), (15, 7)] # forces narrow channel
            },
            "SCENARIO_6": {
                "id": "SCENARIO_6",
                "name": "Scenario 6 — Stress Test (16 Items)",
                "badge": "Heavy Workload",
                "description": "Maximum capacity: 16 items distributed across all quadrants with high corridor traffic, rapid DP optimization, and continuous conflict resolution.",
                "orders": {
                    "R1": ["F1", "F2", "D1", "A3"],
                    "R2": ["H1", "H3", "E2", "C1"],
                    "R3": ["A1", "A2", "B1", "G2"],
                    "R4": ["C3", "C4", "B4", "G3"]
                },
                "dynamic_obstacles": []
            }
        }
