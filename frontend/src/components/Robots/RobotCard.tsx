import React from 'react';
import type { RobotState, RobotId } from '../../types/warehouse';
import { BatteryCharging, Navigation, CheckCircle2, PauseCircle, RefreshCw, Box } from 'lucide-react';

interface RobotCardProps {
  robot: RobotState;
  isSelected: boolean;
  onSelect: (id: RobotId) => void;
}

export const RobotCard: React.FC<RobotCardProps> = ({ robot, isSelected, onSelect }) => {
  const getStatusBadge = () => {
    switch (robot.status) {
      case 'MOVING':
        return {
          bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
          icon: Navigation,
          label: 'NAVIGATING',
        };
      case 'PICKING':
        return {
          bg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
          icon: Box,
          label: 'PICKING ITEM',
        };
      case 'WAITING':
        return {
          bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
          icon: PauseCircle,
          label: 'AISLE WAIT',
        };
      case 'REPLANNING':
        return {
          bg: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
          icon: RefreshCw,
          label: 'A* REPLANNING',
        };
      case 'DELIVERING':
        return {
          bg: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
          icon: Box,
          label: 'OFFLOADING',
        };
      case 'COMPLETED':
        return {
          bg: 'bg-slate-500/10 text-slate-300 border-slate-500/30',
          icon: CheckCircle2,
          label: 'COMPLETED',
        };
      default:
        return {
          bg: 'bg-slate-800 text-slate-400 border-slate-700',
          icon: Navigation,
          label: robot.status,
        };
    }
  };

  const badge = getStatusBadge();
  const StatusIcon = badge.icon;

  return (
    <div
      onClick={() => onSelect(robot.id)}
      className={`p-3.5 rounded-xl border transition-all cursor-pointer select-none backdrop-blur-md ${
        isSelected
          ? 'border-cyan-400 bg-slate-900/90 shadow-lg shadow-cyan-950/40 ring-1 ring-cyan-400'
          : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900/80'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span
            className="w-3.5 h-3.5 rounded-full flex items-center justify-center text-[9px] font-bold text-slate-950 shadow-sm"
            style={{ backgroundColor: robot.color_hex }}
          >
            {robot.id[1]}
          </span>
          <span className="font-mono font-bold text-sm text-slate-200">
            {robot.id} <span className="font-sans font-normal text-xs text-slate-400">({robot.color})</span>
          </span>
        </div>

        <div className={`flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-mono border ${badge.bg}`}>
          <StatusIcon className="w-3 h-3" />
          <span>{badge.label}</span>
        </div>
      </div>

      {/* Target & Coordinates */}
      <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-300 mb-2">
        <div>
          <span className="text-[10px] text-slate-500 block uppercase">Target Destination</span>
          <span className="text-cyan-300 font-semibold truncate block">
            {robot.current_target || 'IDLE / STANDBY'}
          </span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 block uppercase">Grid Position</span>
          <span className="text-slate-300">
            ({robot.grid_x}, {robot.grid_y}) @ {Math.round(robot.heading)}°
          </span>
        </div>
      </div>

      {/* Action Progress Bar (if picking or delivering) */}
      {(robot.status === 'PICKING' || robot.status === 'DELIVERING') && (
        <div className="mb-2">
          <div className="flex justify-between text-[10px] font-mono text-slate-400 mb-1">
            <span>{robot.status === 'PICKING' ? 'PICK DURATION' : 'DELIVERY CONVEYOR'}</span>
            <span>{Math.round(robot.action_progress)}%</span>
          </div>
          <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
            <div
              className={`h-full transition-all duration-150 ${
                robot.status === 'PICKING' ? 'bg-cyan-400' : 'bg-emerald-400'
              }`}
              style={{ width: `${robot.action_progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Telemetry Row */}
      <div className="flex items-center justify-between text-[11px] font-mono pt-2 border-t border-slate-800/80 text-slate-400">
        <div className="flex items-center space-x-1">
          <BatteryCharging className="w-3.5 h-3.5 text-emerald-400" />
          <span>{Math.round(robot.battery)}%</span>
        </div>
        <div>
          <span>{robot.distance.toFixed(1)} m</span>
        </div>
        <div className="text-slate-500">
          <span>{robot.replans} Replans</span>
        </div>
        <div>
          <span className="text-purple-400">{robot.astar_nodes} A* nodes</span>
        </div>
      </div>
    </div>
  );
};
