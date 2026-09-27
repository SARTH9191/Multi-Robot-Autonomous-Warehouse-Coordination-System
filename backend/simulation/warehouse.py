"""
Warehouse Map and Layout Definition
Defines a realistic modern industrial warehouse layout:
- Long shelf blocks (racks) with item storage locations (A1-H4)
- Main horizontal & vertical travel aisles
- Narrow corridors and central cross intersections
- Packing stations, charging docks, loading bays, restricted hazard zones
- Robot starting bays (R1 bottom-left, R2 bottom-right, R3 top-left, R4 top-right)
"""
from typing import Dict, List, Set, Tuple, Any

Point = Tuple[int, int]

class Warehouse:
    def __init__(self, width: int = 32, height: int = 22):
        self.width = width
        self.height = height
        
        # Shelf obstacle cells (robots cannot drive through shelf racks)
        self.shelves: Set[Point] = set()
        # Shelf metadata: { "A1": {"id": "A1", "cell": (4, 4), "pickup_cell": (4, 5), "name": "Electronics Rack A1", "item": "Sensors"} }
        self.shelf_definitions: Dict[str, Dict[str, Any]] = {}
        # Shelf reverse map: pickup_cell -> shelf_id
        self.pickup_to_shelf: Dict[Point, str] = {}
        
        # Key warehouse zones
        self.packing_stations: Dict[str, Point] = {
            "PACK_1": (15, 20),
            "PACK_2": (16, 20)
        }
        self.charging_stations: Dict[str, Point] = {
            "CHARGE_R1": (2, 20),   # Bottom-left
            "CHARGE_R2": (29, 20),  # Bottom-right
            "CHARGE_R3": (2, 1),    # Top-left
            "CHARGE_R4": (29, 1)    # Top-right
        }
        self.dispatch_bays: List[Point] = [(14, 21), (15, 21), (16, 21), (17, 21)]
        self.restricted_zones: Set[Point] = {
            # Staging hazard area near central high-voltage cabinet
            (15, 10), (16, 10), (15, 11), (16, 11)
        }
        
        # Robot initial home start positions (Section 5)
        self.robot_starts: Dict[str, Point] = {
            "R1": (2, 19),   # Bottom-left (Blue)
            "R2": (29, 19),  # Bottom-right (Green)
            "R3": (2, 2),    # Top-left (Yellow)
            "R4": (29, 2)    # Top-right (Red)
        }
        
        # Intersections (key aisle crossroads)
        self.intersections: Set[Point] = set()
        
        # Temporary dynamic obstacles (e.g. spilled pallet or maintenance barrier)
        self.dynamic_obstacles: Set[Point] = set()
        
        self._build_layout()

    def _build_layout(self):
        """Constructs shelf racks and aisle intersections."""
        # 8 Rack clusters (A, B, C, D, E, F, G, H)
        # Each cluster has 4 shelf units with aisles around them.
        
        shelf_blocks = [
            # Cluster A (Top-Left)
            ("A1", (5, 4), (5, 5), "Circuit Boards"),
            ("A2", (6, 4), (6, 5), "Microcontrollers"),
            ("A3", (8, 4), (8, 5), "Camera Modules"),
            ("A4", (9, 4), (9, 5), "LiDAR Sensors"),
            
            # Cluster B (Top-Center-Left)
            ("B1", (12, 4), (12, 5), "Drive Belts"),
            ("B2", (13, 4), (13, 5), "Stepper Motors"),
            ("B3", (18, 4), (18, 5), "Linear Rails"),
            ("B4", (19, 4), (19, 5), "Optical Encoders"),

            # Cluster C (Top-Right)
            ("C1", (22, 4), (22, 5), "Servo Drives"),
            ("C2", (23, 4), (23, 5), "Power Relays"),
            ("C3", (25, 4), (25, 5), "Logic Controllers"),
            ("C4", (26, 4), (26, 5), "CAN Gateways"),

            # Cluster D (Mid-Left)
            ("D1", (5, 9), (5, 8), "Pneumatic Valves"),
            ("D2", (6, 9), (6, 8), "Pressure Regulators"),
            ("D3", (8, 9), (8, 8), "Suction Grippers"),
            ("D4", (9, 9), (9, 8), "Flow Transmitters"),

            # Cluster E (Mid-Right)
            ("E1", (22, 9), (22, 8), "Cooling Fans"),
            ("E2", (23, 9), (23, 8), "Alloy Bearings"),
            ("E3", (25, 9), (25, 8), "Timing Pulleys"),
            ("E4", (26, 9), (26, 8), "Lead Screws"),

            # Cluster F (Lower-Left)
            ("F1", (5, 14), (5, 15), "Lithium Cells"),
            ("F2", (6, 14), (6, 15), "BMS Modules"),
            ("F3", (8, 14), (8, 15), "Inverter Boards"),
            ("F4", (9, 14), (9, 15), "Safety Interlocks"),

            # Cluster G (Lower-Center)
            ("G1", (12, 14), (12, 15), "Fiber Sensors"),
            ("G2", (13, 14), (13, 15), "RFID Scanners"),
            ("G3", (18, 14), (18, 15), "Barcode Units"),
            ("G4", (19, 14), (19, 15), "Emergency Stops"),

            # Cluster H (Lower-Right)
            ("H1", (22, 14), (22, 15), "Aluminum Struts"),
            ("H2", (23, 14), (23, 15), "Fastener Packs"),
            ("H3", (25, 14), (25, 15), "Cable Chains"),
            ("H4", (26, 14), (26, 15), "Mounting Brackets"),
        ]

        for s_id, shelf_cell, pickup_cell, item_name in shelf_blocks:
            self.shelves.add(shelf_cell)
            self.shelf_definitions[s_id] = {
                "id": s_id,
                "cell": shelf_cell,
                "pickup_cell": pickup_cell,
                "name": f"Rack {s_id}",
                "item": item_name
            }
            self.pickup_to_shelf[pickup_cell] = s_id

        # Add additional structural rack obstacles along blocks
        for x in [5, 6, 8, 9, 12, 13, 18, 19, 22, 23, 25, 26]:
            self.shelves.add((x, 3))
            self.shelves.add((x, 10))
            self.shelves.add((x, 13))

        # Strategic cross-aisle intersections
        # Major horizontal aisles: y = 2, y = 6, y = 11, y = 17, y = 19
        # Major vertical aisles: x = 2, x = 10, x = 15, x = 16, x = 21, x = 29
        # Central highway intersection: (15, 11), (16, 11), (10, 11), (21, 11)
        intersection_coords = [
            (2, 6), (10, 6), (15, 6), (16, 6), (21, 6), (29, 6),
            (2, 11), (10, 11), (15, 7), (16, 7), (21, 11), (29, 11),
            (2, 17), (10, 17), (15, 17), (16, 17), (21, 17), (29, 17),
            (10, 2), (21, 2), (10, 19), (21, 19),
            # Narrow bottleneck intersection right in the center aisle
            (15, 12), (16, 12)
        ]
        self.intersections = set(intersection_coords)

    def get_static_obstacles(self) -> Set[Point]:
        """Returns all impassable cells (shelves + perimeter walls + restricted hazard zones)."""
        obs = set(self.shelves)
        obs.update(self.restricted_zones)
        # Perimeter boundaries
        for x in range(self.width):
            obs.add((x, 0))
            obs.add((x, self.height - 1))
        for y in range(self.height):
            obs.add((0, y))
            obs.add((self.width - 1, y))
        return obs

    def get_all_obstacles(self) -> Set[Point]:
        """Static obstacles plus any active dynamic obstacles."""
        obs = self.get_static_obstacles()
        obs.update(self.dynamic_obstacles)
        return obs

    def is_walkable(self, cell: Point) -> bool:
        """Check if cell is within bounds and not blocked."""
        x, y = cell
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return cell not in self.get_all_obstacles()

    def add_dynamic_obstacle(self, cell: Point):
        """Places a temporary blocked barrier."""
        self.dynamic_obstacles.add(cell)

    def clear_dynamic_obstacles(self):
        """Clears all dynamic obstacles."""
        self.dynamic_obstacles.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes warehouse layout for frontend rendering."""
        return {
            "width": self.width,
            "height": self.height,
            "shelves": [
                {
                    "id": s_id,
                    "x": data["cell"][0],
                    "y": data["cell"][1],
                    "pickup_x": data["pickup_cell"][0],
                    "pickup_y": data["pickup_cell"][1],
                    "name": data["name"],
                    "item": data["item"]
                }
                for s_id, data in self.shelf_definitions.items()
            ],
            "structural_shelves": [
                {"x": pt[0], "y": pt[1]}
                for pt in self.shelves
            ],
            "packing_stations": [
                {"id": k, "x": pt[0], "y": pt[1]}
                for k, pt in self.packing_stations.items()
            ],
            "charging_stations": [
                {"id": k, "x": pt[0], "y": pt[1]}
                for k, pt in self.charging_stations.items()
            ],
            "intersections": [
                {"x": pt[0], "y": pt[1]}
                for pt in self.intersections
            ],
            "restricted_zones": [
                {"x": pt[0], "y": pt[1]}
                for pt in self.restricted_zones
            ],
            "dynamic_obstacles": [
                {"x": pt[0], "y": pt[1]}
                for pt in self.dynamic_obstacles
            ]
        }
