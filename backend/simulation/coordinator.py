"""
Multi-Robot Coordinator Engine
Central simulation coordinator managing 4 AGVs, collision detection,
greedy scheduling, dynamic replanning, and real-time state synchronization.
"""
from typing import Dict, List, Set, Tuple, Optional, Any
import time

from .warehouse import Warehouse
from .robot import Robot, RobotStatus
from .order import OrderManager
from ..algorithms.astar import astar_search
from ..algorithms.tsp_dp import solve_tsp_dp
from ..algorithms.collision import (
    detect_vertex_conflicts,
    detect_edge_conflicts,
    detect_intersection_conflicts,
    detect_live_proximities,
    detect_geometric_path_intersections,
    ConflictType
)
from ..algorithms.scheduler import GreedyIntersectionScheduler, SchedulerAction
from ..utils.logger import SimulationLogger, EventLevel
from ..utils.metrics import PerformanceMetrics

Point = Tuple[int, int]

class Coordinator:
    def __init__(self):
        self.warehouse = Warehouse()
        self.logger = SimulationLogger()
        self.metrics = PerformanceMetrics()
        self.scheduler = GreedyIntersectionScheduler(self.warehouse.intersections)
        
        # 4 Autonomous Robots (Section 5)
        self.robots: Dict[str, Robot] = {
            "R1": Robot("R1", "Robot Alpha", "Blue", "#3B82F6", self.warehouse.robot_starts["R1"]),
            "R2": Robot("R2", "Robot Beta", "Green", "#10B981", self.warehouse.robot_starts["R2"]),
            "R3": Robot("R3", "Robot Gamma", "Yellow", "#F59E0B", self.warehouse.robot_starts["R3"]),
            "R4": Robot("R4", "Robot Delta", "Red", "#EF4444", self.warehouse.robot_starts["R4"])
        }
        
        # Simulation playback state
        self.is_running = False
        self.speed_multiplier = 1.0
        self.current_scenario_id = "SCENARIO_1"
        self.active_conflicts: List[Dict[str, Any]] = []
        self.proximity_warnings: List[Dict[str, Any]] = []
        
        # Algorithm inspection cache for Algorithm Visualizer panel
        self.last_astar_visual_data: Dict[str, Any] = {}
        self.last_dp_visual_data: Dict[str, Any] = {}
        self.algorithm_status = {
            "BFS": {"status": "ACTIVE", "desc": "Warehouse reachability & distance matrix precalculated"},
            "A_STAR": {"status": "ACTIVE", "desc": "Dynamic time-space heuristic navigation"},
            "DP_TSP": {"status": "IDLE", "desc": "Held-Karp shelf pickup sequence optimization"},
            "GEOMETRY": {"status": "ACTIVE", "desc": "Continuous proximity & segment intersection checking"},
            "SCHEDULER": {"status": "ACTIVE", "desc": "Greedy priority arbitration & deadlock prevention"},
            "REPLANNER": {"status": "IDLE", "desc": "Dynamic obstacle rerouting"}
        }

        # Initialize with Scenario 1
        self.load_scenario("SCENARIO_1")

    def load_scenario(self, scenario_id: str):
        """Resets and loads one of the 6 predefined course scenarios."""
        scenarios = OrderManager.get_scenario_definitions()
        if scenario_id not in scenarios:
            scenario_id = "SCENARIO_1"
            
        self.current_scenario_id = scenario_id
        scenario = scenarios[scenario_id]
        
        self.is_running = False
        self.logger.reset()
        self.metrics.reset()
        self.active_conflicts.clear()
        self.proximity_warnings.clear()
        
        # Reset dynamic obstacles in warehouse
        self.warehouse.clear_dynamic_obstacles()
        for obs in scenario.get("dynamic_obstacles", []):
            self.warehouse.add_dynamic_obstacle(obs)
            
        # Reset robots to their starting home positions
        for r_id, robot in self.robots.items():
            start_pos = self.warehouse.robot_starts[r_id]
            robot.grid_x, robot.grid_y = start_pos
            robot.x, robot.y = float(start_pos[0]), float(start_pos[1])
            robot.heading = 0.0
            robot.status = RobotStatus.IDLE
            robot.battery = 98.0
            robot.distance_traveled = 0.0
            robot.waiting_ticks = 0
            robot.replan_count = 0
            robot.cargo.clear()
            robot.planned_path.clear()
            robot.path_index = 0
            robot.action_progress = 0.0
            robot.current_target_id = None
            
        # Count total items
        total_items = sum(len(items) for items in scenario["orders"].values())
        self.metrics.total_items_to_pick = total_items
        
        self.logger.log(
            f"Loaded {scenario['name']} ({total_items} items total).",
            level=EventLevel.INFO,
            category="SCENARIO"
        )
        
        # Run DP-TSP optimization for each robot's assigned order list (Section 8)
        self.algorithm_status["DP_TSP"]["status"] = "ACTIVE"
        for r_id, shelf_list in scenario["orders"].items():
            robot = self.robots[r_id]
            packing_pos = self.warehouse.packing_stations["PACK_1"] if r_id in ["R1", "R3"] else self.warehouse.packing_stations["PACK_2"]
            
            opt_shelves, dp_res = OrderManager.optimize_robot_order(
                robot_start=robot.get_pos(),
                shelf_ids=shelf_list,
                packing_station=packing_pos,
                warehouse=self.warehouse
            )
            
            robot.set_order(
                order={"shelves": shelf_list, "packing": packing_pos},
                optimized_sequence=opt_shelves,
                dp_info=dp_res
            )
            
            self.metrics.record_dp_run(dp_res["dp_states_calculated"], dp_res["execution_time_ms"])
            self.last_dp_visual_data[r_id] = dp_res
            
            self.logger.log(
                f"{r_id} DP-TSP optimized route: {dp_res['optimized_cost']} cells (saved {dp_res['saved_distance']} cells, {dp_res['dp_states_calculated']} states in {dp_res['execution_time_ms']}ms)",
                level=EventLevel.INFO,
                robot_id=r_id,
                category="DP_TSP",
                details=dp_res
            )
            
        self.algorithm_status["DP_TSP"]["status"] = "COMPLETED"

    def plan_next_leg_for_robot(self, robot_id: str, is_replan: bool = False):
        """Plans path using A* towards next shelf pickup cell or packing station."""
        robot = self.robots[robot_id]
        curr_pos = robot.get_pos()
        
        # Determine target
        if robot.unvisited_shelves:
            next_shelf_id = robot.unvisited_shelves[0]
            shelf_info = self.warehouse.shelf_definitions[next_shelf_id]
            target_pos = shelf_info["pickup_cell"]
            target_id = next_shelf_id
        elif robot.cargo:
            # Deliver to dedicated packing station bay to prevent bottleneck blocking
            packing_bays = {
                "R1": (14, 20),
                "R3": (15, 20),
                "R4": (16, 20),
                "R2": (17, 20)
            }
            target_pos = packing_bays.get(robot_id, self.warehouse.packing_stations["PACK_1"])
            target_id = "PACKING_STATION"
        else:
            robot.status = RobotStatus.COMPLETED
            return

        robot.current_target_id = target_id
        robot.current_target_pos = target_pos

        # Dynamic obstacles: other robots' current positions to avoid parking inside them
        dyn_obstacles = set()
        for other_id, other_r in self.robots.items():
            if other_id != robot_id and other_r.status in [RobotStatus.WAITING, RobotStatus.PICKING, RobotStatus.DELIVERING, RobotStatus.COMPLETED]:
                dyn_obstacles.add(other_r.get_pos())
                
        # If replanning, optionally reserve currently passing robots' immediate next steps
        reservations = set()
        for other_id, other_r in self.robots.items():
            if other_id != robot_id and other_r.status == RobotStatus.MOVING:
                for idx, step in enumerate(other_r.planned_path[other_r.path_index:other_r.path_index + 6]):
                    reservations.add((step[0], step[1], idx + 1))

        self.algorithm_status["A_STAR"]["status"] = "RUNNING"
        res = astar_search(
            start=curr_pos,
            goal=target_pos,
            width=self.warehouse.width,
            height=self.warehouse.height,
            static_obstacles=self.warehouse.get_all_obstacles(),
            dynamic_obstacles=dyn_obstacles,
            reservations=reservations,
            start_time_tick=0,
            allow_wait=True
        )
        self.algorithm_status["A_STAR"]["status"] = "ACTIVE"

        self.metrics.record_astar_run(res["nodes_explored"], res["execution_time_ms"])
        robot.astar_nodes_explored += res["nodes_explored"]
        self.last_astar_visual_data[robot_id] = res

        if res["found"] and len(res["path"]) > 1:
            robot.planned_path = res["path"]
            robot.path_index = 0
            robot.timed_path = res.get("timed_path", [])
            robot.status = RobotStatus.MOVING
            
            if is_replan:
                robot.replan_count += 1
                self.metrics.path_replans += 1
                self.logger.log(
                    f"{robot_id} replanned new valid path ({res['path_length']} cells, {res['nodes_explored']} nodes in {res['execution_time_ms']}ms)",
                    level=EventLevel.INFO,
                    robot_id=robot_id,
                    category="REPLAN"
                )
            else:
                self.logger.log(
                    f"{robot_id} navigating to {target_id} ({res['path_length']} cells via A*)",
                    level=EventLevel.INFO,
                    robot_id=robot_id,
                    category="NAVIGATION"
                )
        else:
            # Fallback if temporarily blocked: wait 3 ticks then retry
            robot.status = RobotStatus.WAITING
            robot.waiting_ticks += 2
            self.logger.log(
                f"{robot_id} path temporarily blocked to {target_id}, waiting for clearance.",
                level=EventLevel.WARNING,
                robot_id=robot_id,
                category="NAVIGATION"
            )

    def step(self):
        """Executes a single discrete simulation tick."""
        self.metrics.simulation_ticks += 1
        
        # 1. Update robots in IDLE, PICKING, DELIVERING, or WAITING
        for r_id, robot in self.robots.items():
            if robot.status == RobotStatus.IDLE:
                if robot.unvisited_shelves or robot.cargo:
                    self.plan_next_leg_for_robot(r_id, is_replan=False)
                    
            elif robot.status == RobotStatus.PICKING:
                robot.current_action_tick += 1
                robot.action_progress = min(100.0, (robot.current_action_tick / robot.action_duration_ticks) * 100.0)
                if robot.current_action_tick >= robot.action_duration_ticks:
                    picked_shelf = robot.unvisited_shelves.pop(0)
                    shelf_name = self.warehouse.shelf_definitions[picked_shelf]["item"]
                    robot.cargo.append(shelf_name)
                    robot.action_progress = 0.0
                    robot.current_action_tick = 0
                    self.metrics.items_picked_count += 1
                    self.logger.log(
                        f"{r_id} picked {shelf_name} from {picked_shelf}",
                        level=EventLevel.SUCCESS,
                        robot_id=r_id,
                        category="PICKING"
                    )
                    robot.status = RobotStatus.IDLE
                    
            elif robot.status == RobotStatus.DELIVERING:
                robot.current_action_tick += 1
                robot.action_progress = min(100.0, (robot.current_action_tick / robot.action_duration_ticks) * 100.0)
                if robot.current_action_tick >= robot.action_duration_ticks:
                    delivered_count = len(robot.cargo)
                    robot.cargo.clear()
                    robot.action_progress = 0.0
                    robot.current_action_tick = 0
                    self.metrics.orders_completed_count += 1
                    robot.status = RobotStatus.COMPLETED
                    self.logger.log(
                        f"{r_id} delivered {delivered_count} items to Packing Station! Order completed.",
                        level=EventLevel.SUCCESS,
                        robot_id=r_id,
                        category="DELIVERY"
                    )
                    
            elif robot.status == RobotStatus.WAITING:
                robot.waiting_ticks += 1
                self.metrics.total_waiting_seconds += 0.1
                # If waited enough or intersection occupant cleared, attempt replan/resume
                if robot.waiting_ticks % 6 == 0:
                    robot.status = RobotStatus.REPLANNING
                    self.logger.log(
                        f"{r_id} replanning after waiting...",
                        level=EventLevel.INFO,
                        robot_id=r_id,
                        category="SCHEDULER"
                    )
                    self.plan_next_leg_for_robot(r_id, is_replan=True)
                    
            elif robot.status == RobotStatus.REPLANNING:
                self.plan_next_leg_for_robot(r_id, is_replan=True)

        # 2. Collision Detection across all remaining robot trajectories
        trajectories = {}
        for r_id, robot in self.robots.items():
            if robot.status == RobotStatus.MOVING and robot.planned_path:
                trajectories[r_id] = robot.planned_path[robot.path_index:]
            else:
                trajectories[r_id] = [robot.get_pos()]

        v_conflicts = detect_vertex_conflicts(trajectories, horizon=8)
        e_conflicts = detect_edge_conflicts(trajectories, horizon=8)
        i_conflicts = detect_intersection_conflicts(trajectories, self.warehouse.intersections, time_window=2, horizon=10)
        
        all_conflicts = v_conflicts + e_conflicts + i_conflicts
        self.active_conflicts = all_conflicts

        # 3. Continuous Proximity Checks (Computational Geometry)
        pos_dict = {r_id: (r.x, r.y) for r_id, r in self.robots.items()}
        self.proximity_warnings = detect_live_proximities(pos_dict, safety_radius=1.2)

        # 4. Conflict Arbitration via Greedy Scheduler (Section 13, 14, 15)
        if all_conflicts:
            self.metrics.conflicts_detected += len(all_conflicts)
            robot_state_summary = {}
            for r_id, robot in self.robots.items():
                robot_state_summary[r_id] = {
                    "remaining_items": len(robot.unvisited_shelves) + (1 if robot.cargo else 0),
                    "waiting_ticks": robot.waiting_ticks,
                    "dist_to_conflict": 3.0,
                    "battery": robot.battery
                }
                
            decisions = self.scheduler.resolve_conflicts(all_conflicts, robot_state_summary)
            for d in decisions:
                winner = d["winner"]
                loser = d["loser"]
                action = d["action_loser"]
                loc = d["location"]
                
                self.metrics.conflicts_resolved += 1
                self.logger.log(
                    f"⚠ CONFLICT DETECTED {winner} ↔ {loser} near {loc}",
                    level=EventLevel.WARNING,
                    category="CONFLICT"
                )
                self.logger.log(
                    f"✓ {winner} granted priority (Score {d['winner_priority']})",
                    level=EventLevel.SUCCESS,
                    robot_id=winner,
                    category="SCHEDULER"
                )
                
                loser_robot = self.robots[loser]
                if loser_robot.status not in [RobotStatus.PICKING, RobotStatus.DELIVERING, RobotStatus.COMPLETED]:
                    if action == SchedulerAction.HOLD_WAIT:
                        loser_robot.status = RobotStatus.WAITING
                        loser_robot.waiting_ticks += 1
                        self.logger.log(
                            f"⏸ {loser} holding / waiting for corridor clearance",
                            level=EventLevel.INFO,
                            robot_id=loser,
                            category="SCHEDULER"
                        )
                    elif action == SchedulerAction.TRIGGER_REPLAN:
                        loser_robot.status = RobotStatus.REPLANNING
                        self.logger.log(
                            f"↻ {loser} head-on conflict: initiating dynamic A* replan",
                            level=EventLevel.WARNING,
                            robot_id=loser,
                            category="REPLAN"
                        )
                        self.plan_next_leg_for_robot(loser, is_replan=True)

        # 5. Check Deadlock Prevention via DFS Cycle Detection (Section 15)
        deadlock_res = self.scheduler.check_and_resolve_deadlocks({
            r_id: {
                "remaining_items": len(r.unvisited_shelves),
                "waiting_ticks": r.waiting_ticks,
                "dist_to_conflict": 2.0,
                "battery": r.battery
            }
            for r_id, r in self.robots.items()
        })
        
        if deadlock_res:
            victim_id = deadlock_res["victim"]
            self.metrics.deadlocks_detected += 1
            self.metrics.deadlocks_resolved += 1
            self.logger.log(
                f"⚠ DEADLOCK DETECTED among {deadlock_res['cycle']}",
                level=EventLevel.ERROR,
                category="DEADLOCK"
            )
            self.logger.log(
                f"✓ DEADLOCK RESOLVED: Robot {victim_id} ordered to yield and reroute",
                level=EventLevel.SUCCESS,
                robot_id=victim_id,
                category="DEADLOCK"
            )
            victim_robot = self.robots[victim_id]
            victim_robot.status = RobotStatus.REPLANNING
            self.plan_next_leg_for_robot(victim_id, is_replan=True)

        # 6. Advance MOVING robots along their planned path
        for r_id, robot in self.robots.items():
            if robot.status == RobotStatus.MOVING:
                if robot.path_index < len(robot.planned_path):
                    target_step = robot.planned_path[robot.path_index]
                    arrived = robot.step_towards(target_step, move_fraction=0.35 * self.speed_multiplier)
                    
                    if arrived:
                        robot.path_index += 1
                        # If arrived at terminal node of current leg
                        if robot.path_index >= len(robot.planned_path):
                            if robot.current_target_id == "PACKING_STATION":
                                robot.status = RobotStatus.DELIVERING
                                robot.current_action_tick = 0
                                self.logger.log(
                                    f"{r_id} arrived at Packing Station, offloading items...",
                                    level=EventLevel.INFO,
                                    robot_id=r_id,
                                    category="DELIVERY"
                                )
                            else:
                                robot.status = RobotStatus.PICKING
                                robot.current_action_tick = 0
                                self.logger.log(
                                    f"{r_id} reached shelf {robot.current_target_id}, picking items...",
                                    level=EventLevel.INFO,
                                    robot_id=r_id,
                                    category="PICKING"
                                )
                else:
                    robot.status = RobotStatus.IDLE

        # Update total distance
        self.metrics.total_distance_meters = sum(r.distance_traveled for r in self.robots.values())

    def get_state(self) -> Dict[str, Any]:
        """Full simulation state packet for frontend consumption."""
        all_completed = all(r.status == RobotStatus.COMPLETED for r in self.robots.values())
        
        return {
            "timestamp": time.time(),
            "simulation_ticks": self.metrics.simulation_ticks,
            "is_running": self.is_running,
            "speed": self.speed_multiplier,
            "scenario_id": self.current_scenario_id,
            "all_completed": all_completed,
            "robots": [r.to_dict() for r in self.robots.values()],
            "warehouse": self.warehouse.to_dict(),
            "conflicts": self.active_conflicts,
            "proximities": self.proximity_warnings,
            "metrics": self.metrics.to_dict(),
            "recent_events": self.logger.get_recent(25),
            "algorithm_status": self.algorithm_status,
            "last_astar": self.last_astar_visual_data,
            "last_dp": self.last_dp_visual_data
        }
