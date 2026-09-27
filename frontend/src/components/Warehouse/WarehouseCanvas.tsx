import React, { useRef, useEffect, useState } from 'react';
import type { SimulationState, RobotId } from '../../types/warehouse';

interface WarehouseCanvasProps {
  state: SimulationState | null;
  selectedRobotId: RobotId | null;
  onSelectRobot: (id: RobotId | null) => void;
  showAlgoOverlay: boolean;
  activeAlgoTab?: string;
}

export const WarehouseCanvas: React.FC<WarehouseCanvasProps> = ({
  state,
  selectedRobotId,
  onSelectRobot,
  showAlgoOverlay,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Pan and Zoom camera state
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 20, y: 20 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hoveredCell, setHoveredCell] = useState<{ x: number; y: number } | null>(null);

  const cellSize = 38; // base cell size in pixels

  // Mouse wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    setZoom((prev) => Math.max(0.6, Math.min(2.2, prev * factor)));
  };

  // Mouse drag pan
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }

    if (canvasRef.current && state) {
      const rect = canvasRef.current.getBoundingClientRect();
      const mouseX = e.clientX - rect.left - pan.x;
      const mouseY = e.clientY - rect.top - pan.y;
      const gx = Math.floor(mouseX / (cellSize * zoom));
      const gy = Math.floor(mouseY / (cellSize * zoom));

      if (gx >= 0 && gx < state.warehouse.width && gy >= 0 && gy < state.warehouse.height) {
        setHoveredCell({ x: gx, y: gy });
      } else {
        setHoveredCell(null);
      }
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Click on robot or shelf
  const handleClick = (e: React.MouseEvent) => {
    if (!state || !canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left - pan.x;
    const mouseY = e.clientY - rect.top - pan.y;

    // Check if clicked near any robot
    let clickedRobot: RobotId | null = null;
    state.robots.forEach((r) => {
      const rx = (r.x + 0.5) * cellSize * zoom;
      const ry = (r.y + 0.5) * cellSize * zoom;
      const dist = Math.hypot(mouseX - rx, mouseY - ry);
      if (dist < 22 * zoom) {
        clickedRobot = r.id;
      }
    });

    onSelectRobot(clickedRobot);
  };

  const resetCamera = () => {
    setZoom(1.0);
    setPan({ x: 20, y: 20 });
  };

  // Draw simulation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !state) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = state.warehouse.width;
    const height = state.warehouse.height;
    canvas.width = canvas.parentElement?.clientWidth || 1000;
    canvas.height = canvas.parentElement?.clientHeight || 650;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();

    // Apply Camera Pan and Zoom
    ctx.translate(pan.x, pan.y);
    ctx.scale(zoom, zoom);

    const W = width * cellSize;
    const H = height * cellSize;

    // 1. Warehouse Floor (Dark industrial epoxy finish)
    ctx.fillStyle = '#0B0F19';
    ctx.fillRect(0, 0, W, H);

    // Floor grid tiles
    ctx.strokeStyle = '#161F33';
    ctx.lineWidth = 1;
    for (let x = 0; x <= width; x++) {
      ctx.beginPath();
      ctx.moveTo(x * cellSize, 0);
      ctx.lineTo(x * cellSize, H);
      ctx.stroke();
    }
    for (let y = 0; y <= height; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * cellSize);
      ctx.lineTo(W, y * cellSize);
      ctx.stroke();
    }

    // 2. Aisle Markings (Center highway dashed lines)
    ctx.strokeStyle = '#27354E';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    // Main vertical highways: x = 10, x = 15.5, x = 21
    [10.5, 15.5, 21.5].forEach((gx) => {
      ctx.beginPath();
      ctx.moveTo(gx * cellSize, 2 * cellSize);
      ctx.lineTo(gx * cellSize, (height - 2) * cellSize);
      ctx.stroke();
    });
    // Main horizontal aisles: y = 6.5, y = 11.5, y = 17.5
    [6.5, 11.5, 17.5].forEach((gy) => {
      ctx.beginPath();
      ctx.moveTo(2 * cellSize, gy * cellSize);
      ctx.lineTo((width - 2) * cellSize, gy * cellSize);
      ctx.stroke();
    });
    ctx.setLineDash([]);

    // 3. Restricted Hazard Zones (Yellow-Black Caution Stripes)
    state.warehouse.restricted_zones.forEach((rz) => {
      const rx = rz.x * cellSize;
      const ry = rz.y * cellSize;
      ctx.fillStyle = '#2A2004';
      ctx.fillRect(rx, ry, cellSize, cellSize);

      ctx.save();
      ctx.beginPath();
      ctx.rect(rx, ry, cellSize, cellSize);
      ctx.clip();
      ctx.strokeStyle = '#EAB308';
      ctx.lineWidth = 3;
      for (let d = -cellSize; d < cellSize * 2; d += 8) {
        ctx.beginPath();
        ctx.moveTo(rx + d, ry);
        ctx.lineTo(rx + d + cellSize, ry + cellSize);
        ctx.stroke();
      }
      ctx.restore();

      ctx.strokeStyle = '#FACC15';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(rx + 1, ry + 1, cellSize - 2, cellSize - 2);
    });

    // 4. Charging Docks (Cyan glowing dock pads)
    state.warehouse.charging_stations.forEach((cs) => {
      const cx = cs.x * cellSize;
      const cy = cs.y * cellSize;
      ctx.fillStyle = '#062B33';
      ctx.fillRect(cx + 2, cy + 2, cellSize - 4, cellSize - 4);
      ctx.strokeStyle = '#06B6D4';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(cx + 2, cy + 2, cellSize - 4, cellSize - 4);

      // Lightning Bolt Icon
      ctx.fillStyle = '#22D3EE';
      ctx.font = '13px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('⚡', cx + cellSize / 2, cy + cellSize / 2);
    });

    // 5. Packing / Dispatch Stations
    state.warehouse.packing_stations.forEach((ps) => {
      const px = ps.x * cellSize;
      const py = ps.y * cellSize;
      ctx.fillStyle = '#064E3B';
      ctx.fillRect(px + 2, py + 2, cellSize - 4, cellSize - 4);
      ctx.strokeStyle = '#10B981';
      ctx.lineWidth = 2;
      ctx.strokeRect(px + 2, py + 2, cellSize - 4, cellSize - 4);

      ctx.fillStyle = '#34D399';
      ctx.font = 'bold 9px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('PACK', px + cellSize / 2, py + cellSize / 2 - 4);
      ctx.fillText('STATION', px + cellSize / 2, py + cellSize / 2 + 6);
    });

    // 6. Shelves / Racks (Heavy industrial multi-tier racks)
    const shelfMap = new Map();
    state.warehouse.shelves.forEach((s) => shelfMap.set(`${s.x},${s.y}`, s));

    // Structural rack blocks
    state.warehouse.structural_shelves.forEach((st) => {
      const sx = st.x * cellSize;
      const sy = st.y * cellSize;
      const sKey = `${st.x},${st.y}`;
      const shelfData = shelfMap.get(sKey);

      // Shelf base shadow
      ctx.fillStyle = '#0D1424';
      ctx.fillRect(sx + 3, sy + 3, cellSize - 6, cellSize - 6);

      // Steel rack framework
      ctx.fillStyle = '#1E293B';
      ctx.fillRect(sx + 2, sy + 2, cellSize - 4, cellSize - 4);
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(sx + 2, sy + 2, cellSize - 4, cellSize - 4);

      // Shelf inventory boxes
      ctx.fillStyle = '#B45309'; // Cardboard brown pallet
      ctx.fillRect(sx + 6, sy + 6, (cellSize - 12) / 2, cellSize - 12);
      ctx.fillStyle = '#92400E';
      ctx.fillRect(sx + 6 + (cellSize - 12) / 2 + 2, sy + 6, (cellSize - 12) / 2 - 2, cellSize - 12);

      if (shelfData) {
        // Shelf ID badge
        ctx.fillStyle = '#0F172A';
        ctx.fillRect(sx + 4, sy + cellSize - 13, cellSize - 8, 10);
        ctx.fillStyle = '#38BDF8';
        ctx.font = 'bold 8px Inter, monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(shelfData.id, sx + cellSize / 2, sy + cellSize - 8);
      }
    });

    // 7. Dynamic Obstacles (e.g. temporary maintenance barrier/spill in Scenario 4)
    state.warehouse.dynamic_obstacles.forEach((obs) => {
      const ox = obs.x * cellSize;
      const oy = obs.y * cellSize;
      ctx.fillStyle = '#7C2D12';
      ctx.fillRect(ox + 3, oy + 3, cellSize - 6, cellSize - 6);
      ctx.strokeStyle = '#F97316';
      ctx.lineWidth = 2;
      ctx.strokeRect(ox + 3, oy + 3, cellSize - 6, cellSize - 6);
      ctx.fillStyle = '#FFEDD5';
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('🚧', ox + cellSize / 2, oy + cellSize / 2);
    });

    // 8. Intersections (Crossroad markers)
    state.warehouse.intersections.forEach((inter) => {
      const ix = (inter.x + 0.5) * cellSize;
      const iy = (inter.y + 0.5) * cellSize;
      ctx.fillStyle = 'rgba(148, 163, 184, 0.15)';
      ctx.beginPath();
      ctx.arc(ix, iy, 4, 0, Math.PI * 2);
      ctx.fill();
    });

    // 9. Algorithm Visualization Overlay (A* Open/Closed Sets or Wavefront)
    if (showAlgoOverlay && state.last_astar) {
      // Pick selected robot or R1
      const activeAStarRobot = selectedRobotId || 'R1';
      const astarData = state.last_astar[activeAStarRobot];
      if (astarData) {
        // Closed nodes: Lavender / Violet dots
        ctx.fillStyle = 'rgba(139, 92, 246, 0.25)';
        astarData.closed_nodes.forEach((cn) => {
          ctx.fillRect(cn[0] * cellSize + 4, cn[1] * cellSize + 4, cellSize - 8, cellSize - 8);
        });

        // Open nodes: Cyan / Green dots
        ctx.fillStyle = 'rgba(52, 211, 153, 0.45)';
        astarData.open_nodes.forEach((on) => {
          ctx.beginPath();
          ctx.arc((on[0] + 0.5) * cellSize, (on[1] + 0.5) * cellSize, 4, 0, Math.PI * 2);
          ctx.fill();
        });
      }
    }

    // 10. Robot Planned Paths (Glowing lines with waypoint dots)
    state.robots.forEach((r) => {
      if (r.path && r.path.length > 0) {
        const isSelected = selectedRobotId === r.id;
        ctx.strokeStyle = r.color_hex;
        ctx.lineWidth = isSelected ? 3.5 : 2.0;
        ctx.globalAlpha = isSelected ? 0.95 : 0.45;
        ctx.setLineDash([5, 3]);

        ctx.beginPath();
        // Start from current continuous position
        ctx.moveTo((r.x + 0.5) * cellSize, (r.y + 0.5) * cellSize);
        r.path.forEach((pt) => {
          ctx.lineTo((pt[0] + 0.5) * cellSize, (pt[1] + 0.5) * cellSize);
        });
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.globalAlpha = 1.0;

        // Target waypoint pulse
        if (r.path.length > 0) {
          const dest = r.path[r.path.length - 1];
          ctx.fillStyle = r.color_hex;
          ctx.beginPath();
          ctx.arc((dest[0] + 0.5) * cellSize, (dest[1] + 0.5) * cellSize, 5, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    });

    // 11. Active Conflicts & Warning Rings (Sections 11 & 12)
    state.conflicts.forEach((conf) => {
      if (conf.location) {
        const cx = (conf.location[0] + 0.5) * cellSize;
        const cy = (conf.location[1] + 0.5) * cellSize;

        // Animated warning pulse ring
        const pulse = (Date.now() / 250) % 1;
        ctx.strokeStyle = '#EF4444';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(cx, cy, 14 + pulse * 10, 0, Math.PI * 2);
        ctx.stroke();

        ctx.fillStyle = '#EF4444';
        ctx.beginPath();
        ctx.arc(cx, cy, 6, 0, Math.PI * 2);
        ctx.fill();

        // Conflict Tag
        ctx.fillStyle = '#DC2626';
        ctx.font = 'bold 9px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('⚠ CONFLICT', cx, cy - 16);
      }
    });

    // 12. Continuous Proximity Warning Lines
    state.proximities.forEach((prox) => {
      const r1 = state.robots.find((r) => r.id === prox.robots[0]);
      const r2 = state.robots.find((r) => r.id === prox.robots[1]);
      if (r1 && r2) {
        ctx.strokeStyle = '#F59E0B';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.moveTo((r1.x + 0.5) * cellSize, (r1.y + 0.5) * cellSize);
        ctx.lineTo((r2.x + 0.5) * cellSize, (r2.y + 0.5) * cellSize);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // 13. Render Autonomous Robots (AGVs) - Detailed Realistic Industrial Model (Section 5)
    state.robots.forEach((robot) => {
      const centerX = (robot.x + 0.5) * cellSize;
      const centerY = (robot.y + 0.5) * cellSize;
      const isSelected = selectedRobotId === robot.id;

      ctx.save();
      ctx.translate(centerX, centerY);

      // LiDAR Sensor Radar Cone (Semi-transparent arc forward)
      ctx.rotate((robot.heading * Math.PI) / 180);

      ctx.fillStyle = `${robot.color_hex}1A`; // ~10% opacity cone
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, 36, -Math.PI / 4, Math.PI / 4);
      ctx.closePath();
      ctx.fill();

      // Front Headlight Beams
      ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
      ctx.beginPath();
      ctx.moveTo(12, -5);
      ctx.lineTo(26, -10);
      ctx.lineTo(26, 10);
      ctx.lineTo(12, 5);
      ctx.closePath();
      ctx.fill();

      // 4 Wheels (Black industrial rubber tires)
      ctx.fillStyle = '#090D16';
      // Front-left, Front-right, Rear-left, Rear-right
      ctx.fillRect(6, -15, 6, 3);
      ctx.fillRect(6, 12, 6, 3);
      ctx.fillRect(-12, -15, 6, 3);
      ctx.fillRect(-12, 12, 6, 3);

      // AGV Chassis (Rounded rectangle)
      const w = 26;
      const h = 22;
      const radius = 5;

      // Chassis shadow
      ctx.fillStyle = 'rgba(0,0,0,0.5)';
      ctx.beginPath();
      ctx.roundRect(-w / 2 + 1, -h / 2 + 1, w, h, radius);
      ctx.fill();

      // Main Chassis Body
      ctx.fillStyle = '#1E293B';
      ctx.beginPath();
      ctx.roundRect(-w / 2, -h / 2, w, h, radius);
      ctx.fill();

      // Colored bumper stripe matching robot identity
      ctx.strokeStyle = robot.color_hex;
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.stroke();

      // Small Cargo Pallet / Box on rear if carrying items
      if (robot.cargo && robot.cargo.length > 0) {
        ctx.fillStyle = '#F59E0B'; // Amber cargo box
        ctx.fillRect(-10, -6, 10, 12);
        ctx.strokeStyle = '#78350F';
        ctx.lineWidth = 1;
        ctx.strokeRect(-10, -6, 10, 12);
      }

      // Front Direction Indicator
      ctx.fillStyle = '#FFFFFF';
      ctx.beginPath();
      ctx.moveTo(8, 0);
      ctx.lineTo(3, -4);
      ctx.lineTo(3, 4);
      ctx.closePath();
      ctx.fill();

      // Rotate back to draw text labels upright
      ctx.rotate((-robot.heading * Math.PI) / 180);

      // Robot ID text
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 10px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(robot.id, 0, 0);

      // Status indicator badge
      let statusColor = '#10B981'; // Green for MOVING
      if (robot.status === 'WAITING') statusColor = '#F59E0B'; // Orange
      if (robot.status === 'REPLANNING') statusColor = '#8B5CF6'; // Purple
      if (robot.status === 'PICKING') statusColor = '#06B6D4'; // Cyan
      if (robot.status === 'DELIVERING') statusColor = '#3B82F6'; // Blue
      if (robot.status === 'COMPLETED') statusColor = '#64748B'; // Slate

      // Status LED indicator dot
      ctx.fillStyle = statusColor;
      ctx.beginPath();
      ctx.arc(0, -15, 3.5, 0, Math.PI * 2);
      ctx.fill();

      // Action Progress Bar (for PICKING and DELIVERING)
      if ((robot.status === 'PICKING' || robot.status === 'DELIVERING') && robot.action_progress > 0) {
        const barW = 28;
        const barH = 4;
        ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
        ctx.fillRect(-barW / 2, 14, barW, barH);
        ctx.fillStyle = robot.status === 'PICKING' ? '#06B6D4' : '#10B981';
        ctx.fillRect(-barW / 2, 14, (barW * robot.action_progress) / 100, barH);
        ctx.strokeStyle = '#334155';
        ctx.strokeRect(-barW / 2, 14, barW, barH);
      }

      // Selection Halo
      if (isSelected) {
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([3, 2]);
        ctx.beginPath();
        ctx.arc(0, 0, 20, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      ctx.restore();
    });

    // Hovered grid cell coordinates
    if (hoveredCell) {
      const hx = hoveredCell.x * cellSize;
      const hy = hoveredCell.y * cellSize;
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
      ctx.lineWidth = 1;
      ctx.strokeRect(hx, hy, cellSize, cellSize);
    }

    ctx.restore();
  }, [state, selectedRobotId, zoom, pan, isDragging, hoveredCell, showAlgoOverlay]);

  return (
    <div className="relative w-full h-full bg-slate-950 overflow-hidden select-none border border-slate-800 rounded-xl">
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-crosshair block"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onClick={handleClick}
      />

      {/* Floating Canvas Camera & Coordinate HUD */}
      <div className="absolute bottom-4 left-4 flex items-center space-x-2 bg-slate-900/90 backdrop-blur border border-slate-700/80 px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 shadow-xl">
        <span>ZOOM: {Math.round(zoom * 100)}%</span>
        <span className="text-slate-600">|</span>
        {hoveredCell ? (
          <span className="text-cyan-400">
            GRID: ({hoveredCell.x}, {hoveredCell.y})
          </span>
        ) : (
          <span className="text-slate-500">HOVER CELL</span>
        )}
        <span className="text-slate-600">|</span>
        <button
          onClick={resetCamera}
          className="text-cyan-400 hover:text-cyan-300 transition-colors uppercase font-sans text-[11px]"
        >
          Reset Camera
        </button>
      </div>

      {/* Legend overlay */}
      <div className="absolute top-4 right-4 flex flex-col space-y-1.5 bg-slate-900/85 backdrop-blur border border-slate-800 p-2.5 rounded-lg text-[11px] text-slate-300 pointer-events-none shadow-xl">
        <div className="font-semibold text-[10px] uppercase tracking-wider text-slate-400 mb-0.5">
          Map Legend
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 bg-blue-500 rounded-sm"></span>
          <span>R1 Alpha (Blue)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 bg-emerald-500 rounded-sm"></span>
          <span>R2 Beta (Green)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 bg-amber-500 rounded-sm"></span>
          <span>R3 Gamma (Yellow)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 bg-red-500 rounded-sm"></span>
          <span>R4 Delta (Red)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 bg-emerald-700 border border-emerald-400 rounded-sm"></span>
          <span>Packing Docks</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 bg-cyan-900 border border-cyan-400 rounded-sm"></span>
          <span>Charging Pads</span>
        </div>
      </div>
    </div>
  );
};
