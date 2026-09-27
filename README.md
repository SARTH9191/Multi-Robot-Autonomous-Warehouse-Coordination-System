# Autonomous Warehouse Multi-Robot Coordination System

> **Design and Analysis of Algorithms (DAA) Capstone Project**  
> A production-quality, real-time autonomous warehouse simulator featuring 4 Autonomous Guided Vehicles (AGVs) navigating a large warehouse using manually implemented algorithms.

---

## 1. System Architecture & Tech Stack

```text
React 19 Frontend (HTML5 Canvas, Lucide, Tailwind CSS)
                       │
                       │ WebSocket (ws://localhost:8000/ws) & REST
                       ▼
FastAPI Backend (Asyncio 25Hz Clock Engine)
                       │
                       ├── Warehouse Graph & Environment Model
                       ├── Multi-Robot Coordinator
                       │        │
                       │        ├── True A* Pathfinding Engine (f = g + h)
                       │        ├── Held-Karp Dynamic Programming (DP-TSP)
                       │        ├── Computational Geometry (Segment Intersection & Proximity)
                       │        ├── Greedy Aisle & Intersection Scheduler
                       │        └── DFS Deadlock Wait-For Cycle Detector
                       ▼
Telemetry, Odometry & Live Performance Aggregator
```

### Core Technologies
- **Frontend**: React 19, TypeScript, Vite, HTML5 Canvas (high-efficiency 60 FPS drawing), Tailwind CSS v4, Lucide React icons, Canvas Confetti.
- **Backend**: Python 3.14 / uv, FastAPI, WebSockets, Pydantic, Pytest.
- **Algorithms**: 100% manually implemented — **Zero external blackbox routing libraries**.

---

## 2. Four Algorithmic Paradigms (DAA Viva Breakdown)

### 1. Graph Algorithms: BFS, DFS, and True A*
- **Breadth-First Search (BFS)**:
  - Precomputes reachability, shortest hops between aisle nodes, and warehouse distance matrices for the TSP order optimizer.
  - Implemented in `backend/algorithms/bfs.py`.
- **Depth-First Search (DFS)**:
  - Directed 3-color graph traversal to detect cycles in wait-for dependency chains (Deadlock Detection & Prevention).
  - Implemented in `backend/algorithms/dfs.py`.
- **A\* Pathfinding ($f(n) = g(n) + h(n)$)**:
  - Uses Manhattan distance heuristic $h(A, B) = |x_1 - x_2| + |y_1 - y_2|$ for 4-direction grid movement.
  - Supports static rack obstacles, dynamic robot locations, and time-space reservation tables $(x, y, t)$ to avoid vertex and edge swap collisions.
  - Implemented in `backend/algorithms/astar.py`.

### 2. Dynamic Programming: Held-Karp DP-TSP Order Optimization
- **Recurrence Formulation**:
  $$\text{DP}[\text{mask}][i] = \min_{j \in \text{mask} \setminus \{i\}} \left( \text{DP}[\text{mask} \setminus \{i\}][j] + \text{dist}(j, i) \right)$$
  - Base case: $\text{DP}[1 \ll i][i] = \text{dist}(\text{Start}, \text{Shelf}_i)$.
  - Final destination: $\min_i \left( \text{DP}[(1 \ll n) - 1][i] + \text{dist}(\text{Shelf}_i, \text{PackingStation}) \right)$.
  - Exact bitmask subset formulation with parent pointer array for $O(n)$ route reconstruction.
  - Implemented in `backend/algorithms/tsp_dp.py`.

### 3. Computational Geometry: Orientation & Line Segment Intersection
- **Orientation Function**:
  $$\text{val} = (q.y - p.y) \cdot (r.x - q.x) - (q.x - p.x) \cdot (r.y - q.y)$$
  - `0` $\to$ Collinear, `1` $\to$ Clockwise, `2` $\to$ Counterclockwise.
- **Segment Intersection**:
  - Validates general cases via differing orientations and boundary bounding boxes for overlapping collinear cases.
  - Real-time continuous Euclidean proximity detector ($d < \text{safetyDistance}$).
  - Implemented in `backend/algorithms/geometry.py` and `backend/algorithms/collision.py`.

### 4. Greedy Algorithms: Aisle & Intersection Conflict-Free Scheduler
- **Greedy Priority Formula**:
  $$\text{Priority} = (\text{Urgency} \times 10) + (\text{WaitingTicks} \times 2.5) - (\text{DistanceToBottleneck} \times 0.8) + (100 - \text{Battery}) \times 0.05$$
  - Resolves vertex collisions, edge swaps, and bottleneck corridor convergence.
  - Grants passage to the highest priority AGV while holding or rerouting the conflicting AGV via dynamic A\* replanning.
  - Implemented in `backend/algorithms/scheduler.py`.

---

## 3. Four Autonomous AGVs (Fleet Setup)

| Robot ID | Name | Theme Color | Starting Home | Initial Focus |
|:---:|:---:|:---:|:---:|:---:|
| **R1** | Robot Alpha | **Blue** (`#3B82F6`) | Bottom-Left `(2, 19)` | Quadrant F & A |
| **R2** | Robot Beta | **Green** (`#10B981`) | Bottom-Right `(29, 19)` | Quadrant H & C |
| **R3** | Robot Gamma | **Yellow** (`#F59E0B`) | Top-Left `(2, 2)` | Quadrant A & D |
| **R4** | Robot Delta | **Red** (`#EF4444`) | Top-Right `(29, 2)` | Quadrant C & E |

Each AGV features:
- Rounded industrial chassis with 4 rubber tires.
- Front directional headlights and LiDAR perception radar cone.
- Real-time continuous coordinate interpolation (no cell teleportation).
- Dynamic action progress bar for item picking and packing offload.

---

## 4. Predefined Course Demonstration Scenarios

1. **Scenario 1 — Normal Operation**: Standard multi-robot warehouse routing across 4 quadrants.
2. **Scenario 2 — Intersection Conflict**: 2 robots converge simultaneously at central intersection `(15, 11)`.
3. **Scenario 3 — Four Robot Conflict**: Core DAA Demo — all 4 AGVs converge on the central highway bottleneck corridor simultaneously.
4. **Scenario 4 — Dynamic Obstacle**: A simulated aisle spill blocks the northern corridor; robots detect the obstruction and dynamically recalculate paths.
5. **Scenario 5 — Deadlock Detection & Yield**: Head-on confrontation in a narrow single-lane aisle; DFS cycle detector identifies the wait-for deadlock and orders the lowest-priority robot to yield.
6. **Scenario 6 — Stress Test (16 Items)**: High throughput operation with 16 distributed items across all storage racks.

---

## 5. Running the Project Locally

### Prerequisites
- Node.js (v18+)
- Python (3.11+) or `uv`

### 1. Run Unit Tests (15 Tests)
```powershell
& "backend\.venv\Scripts\pytest.exe" -v
```

### 2. Start FastAPI Backend
```powershell
& "backend\.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 3. Start Frontend Dashboard
```powershell
cd frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 6. Project Controls & Shortcuts
- `Spacebar`: Start / Pause simulation
- `S`: Single-step tick (Step-by-step presentation mode)
- `R`: Reset current scenario
- `Speed`: `0.5x`, `1.0x`, `2.0x`, `4.0x`
- `Algo Trace`: Toggle A\* open/closed exploration wavefront on canvas
- `DAA Report`: View full viva performance report & bar charts
