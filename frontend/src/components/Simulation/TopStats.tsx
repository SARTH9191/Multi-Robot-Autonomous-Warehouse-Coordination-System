import React from 'react';
import type { PerformanceMetrics, RobotState } from '../../types/warehouse';
import { 
  Bot, 
  Package, 
  ShieldCheck, 
  AlertTriangle, 
  RefreshCw, 
  Milestone, 
  Clock 
} from 'lucide-react';

interface TopStatsProps {
  metrics: PerformanceMetrics;
  robots: RobotState[];
  isOnline: boolean;
}

export const TopStats: React.FC<TopStatsProps> = ({ metrics, robots, isOnline }) => {
  const activeCount = robots.filter(
    (r) => r.status === 'MOVING' || r.status === 'PICKING' || r.status === 'DELIVERING' || r.status === 'REPLANNING'
  ).length;

  const seconds = metrics.simulation_ticks * 0.04;
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  const timeFormatted = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

  const cards = [
    {
      label: 'ROBOTS',
      value: `${robots.length}`,
      sub: `${activeCount} ACTIVE`,
      icon: Bot,
      color: 'text-blue-400',
      border: 'border-blue-500/20',
      bg: 'bg-blue-950/20'
    },
    {
      label: 'ITEM CARGO',
      value: `${metrics.items_picked} / ${metrics.total_items}`,
      sub: `${metrics.orders_completed} DELIVERED`,
      icon: Package,
      color: 'text-cyan-400',
      border: 'border-cyan-500/20',
      bg: 'bg-cyan-950/20'
    },
    {
      label: 'COLLISIONS',
      value: `${metrics.collisions}`,
      sub: 'ZERO INCIDENTS',
      icon: ShieldCheck,
      color: 'text-emerald-400',
      border: 'border-emerald-500/30',
      bg: 'bg-emerald-950/20'
    },
    {
      label: 'CONFLICTS',
      value: `${metrics.conflicts_detected}`,
      sub: `${metrics.conflicts_resolved} RESOLVED`,
      icon: AlertTriangle,
      color: 'text-amber-400',
      border: 'border-amber-500/20',
      bg: 'bg-amber-950/20'
    },
    {
      label: 'PATH REPLANS',
      value: `${metrics.path_replans}`,
      sub: `${metrics.deadlocks_resolved} DEADLOCKS YIELDED`,
      icon: RefreshCw,
      color: 'text-purple-400',
      border: 'border-purple-500/20',
      bg: 'bg-purple-950/20'
    },
    {
      label: 'ODOMETRY',
      value: `${metrics.total_distance_m} m`,
      sub: `${metrics.total_waiting_sec}s WAIT TIME`,
      icon: Milestone,
      color: 'text-slate-300',
      border: 'border-slate-700/40',
      bg: 'bg-slate-900/40'
    },
    {
      label: 'SIM TIME',
      value: timeFormatted,
      sub: isOnline ? '25 Hz TICK' : 'OFFLINE',
      icon: Clock,
      color: isOnline ? 'text-emerald-400' : 'text-red-400',
      border: 'border-slate-700/40',
      bg: 'bg-slate-900/40'
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`flex flex-col justify-between p-3 rounded-xl border backdrop-blur-md transition-all hover:scale-[1.02] ${card.border} ${card.bg}`}
          >
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-[10px] font-mono tracking-wider font-semibold uppercase">
                {card.label}
              </span>
              <Icon className={`w-4 h-4 ${card.color}`} />
            </div>
            <div className={`text-lg font-bold font-mono tracking-tight ${card.color}`}>
              {card.value}
            </div>
            <div className="text-[10px] font-mono text-slate-400 uppercase tracking-tight mt-0.5 truncate">
              {card.sub}
            </div>
          </div>
        );
      })}
    </div>
  );
};
