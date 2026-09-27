"""
Computational Geometry Module
Implements exact orientation, segment intersection, and proximity detection.
"""
from typing import Tuple, Dict, Any
import math

Point = Tuple[float, float]

def orientation(p: Point, q: Point, r: Point) -> int:
    """
    Find orientation of ordered triplet (p, q, r).
    0 -> p, q, r are collinear
    1 -> Clockwise
    2 -> Counterclockwise
    
    Cross product: (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if abs(val) < 1e-9:
        return 0
    return 1 if val > 0 else 2

def on_segment(p: Point, q: Point, r: Point) -> bool:
    """Check if point q lies on line segment 'pr'."""
    return (q[0] <= max(p[0], r[0]) + 1e-9 and q[0] >= min(p[0], r[0]) - 1e-9 and
            q[1] <= max(p[1], r[1]) + 1e-9 and q[1] >= min(p[1], r[1]) - 1e-9)

def segments_intersect(p1: Point, q1: Point, p2: Point, q2: Point) -> bool:
    """
    Returns True if line segment 'p1q1' and 'p2q2' intersect.
    """
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if o1 != o2 and o3 != o4:
        return True

    # Special Cases (Collinear and overlapping)
    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    if o2 == 0 and on_segment(p1, q2, q1):
        return True
    if o3 == 0 and on_segment(p2, p1, q2):
        return True
    if o4 == 0 and on_segment(p2, q1, q2):
        return True

    return False

def euclidean_distance(p1: Point, p2: Point) -> float:
    """Euclidean distance between two 2D points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def manhattan_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    """Manhattan distance for grid-based pathfinding."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def check_proximity(pos_a: Point, pos_b: Point, safety_distance: float = 1.2) -> Tuple[bool, float]:
    """
    Check if two robots violate safety distance radius.
    Returns (is_violated, distance).
    """
    dist = euclidean_distance(pos_a, pos_b)
    return dist < safety_distance, dist

def intersection_point(p1: Point, p2: Point, p3: Point, p4: Point) -> Tuple[float, float] | None:
    """
    Compute intersection point of lines p1-p2 and p3-p4 if segments intersect.
    """
    if not segments_intersect(p1, p2, p3, p4):
        return None
    
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-9:
        # Collinear or parallel
        return ((x1 + x2 + x3 + x4) / 4.0, (y1 + y2 + y3 + y4) / 4.0)
    
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    return (round(px, 3), round(py, 3))
