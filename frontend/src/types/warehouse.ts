export type RobotId = 'R1' | 'R2' | 'R3' | 'R4';

export type RobotStatus = 
  | 'IDLE'
  | 'MOVING'
  | 'PICKING'
  | 'WAITING'
  | 'REPLANNING'
  | 'DELIVERING'
  | 'CHARGING'
  | 'COMPLETED';

export interface ShelfInfo {
  id: string;
  x: number;
  y: number;
  pickup_x: number;
  pickup_y: number;
  name: string;
  item: string;
}

export interface ZoneCoord {
  id?: string;
  x: number;
  y: number;
}

export interface WarehouseLayout {
  width: number;
  height: number;
  shelves: ShelfInfo[];
  structural_shelves: { x: number; y: number }[];
  packing_stations: ZoneCoord[];
  charging_stations: ZoneCoord[];
  intersections: { x: number; y: number }[];
  restricted_zones: { x: number; y: number }[];
  dynamic_obstacles: { x: number; y: number }[];
}

export interface DpInfo {
  optimal_sequence: number[];
  optimal_positions: [number, number][];
  original_cost: number;
  optimized_cost: number;
  saved_distance: number;
  dp_states_calculated: number;
  execution_time_ms: number;
  dp_table_size: string;
  is_exact_dp: boolean;
}

export interface RobotState {
  id: RobotId;
  name: string;
  color: string;
  color_hex: string;
  x: number;
  y: number;
  grid_x: number;
  grid_y: number;
  heading: number;
  status: RobotStatus;
  battery: number;
  distance: number;
  waiting_ticks: number;
  replans: number;
  current_target: string | null;
  unvisited_count: number;
  cargo: string[];
  action_progress: number;
  path: [number, number][];
  astar_nodes: number;
  dp_info: DpInfo | null;
}

export interface SimulationEvent {
  id: number;
  timestamp: string;
  time_seconds: number;
  level: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  robot_id?: string;
  category: string;
  message: string;
  details?: Record<string, any>;
}

export interface PerformanceMetrics {
  simulation_ticks: number;
  total_distance_m: number;
  total_waiting_sec: number;
  conflicts_detected: number;
  conflicts_resolved: number;
  path_replans: number;
  collisions: number;
  deadlocks_detected: number;
  deadlocks_resolved: number;
  total_items: number;
  items_picked: number;
  orders_completed: number;
  astar_runs: number;
  astar_total_nodes: number;
  avg_planning_time_ms: number;
  dp_states_total: number;
  avg_dp_time_ms: number;
}

export interface ConflictRecord {
  type: string;
  time_step?: number;
  robots: string[];
  location?: [number, number];
  edge?: [[number, number], [number, number]];
  description?: string;
}

export interface ProximityRecord {
  type: string;
  robots: string[];
  distance: number;
  safety_radius: number;
  description: string;
}

export interface AlgorithmStatusItem {
  status: 'ACTIVE' | 'RUNNING' | 'IDLE' | 'COMPLETED';
  desc: string;
}

export interface AStarSample {
  found: boolean;
  path: [number, number][];
  cost: number;
  nodes_explored: number;
  open_nodes: [number, number][];
  closed_nodes: [number, number][];
  execution_time_ms: number;
}

export interface SimulationState {
  timestamp: number;
  simulation_ticks: number;
  is_running: boolean;
  speed: number;
  scenario_id: string;
  all_completed: boolean;
  robots: RobotState[];
  warehouse: WarehouseLayout;
  conflicts: ConflictRecord[];
  proximities: ProximityRecord[];
  metrics: PerformanceMetrics;
  recent_events: SimulationEvent[];
  algorithm_status: Record<string, AlgorithmStatusItem>;
  last_astar: Record<string, AStarSample>;
  last_dp: Record<string, DpInfo>;
}

export interface ScenarioDefinition {
  id: string;
  name: string;
  badge: string;
  description: string;
  orders: Record<string, string[]>;
  dynamic_obstacles: [number, number][];
}
