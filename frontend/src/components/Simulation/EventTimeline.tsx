import React, { useRef, useEffect } from 'react';
import type { SimulationEvent } from '../../types/warehouse';
import { Terminal, CheckCircle2, AlertTriangle, AlertOctagon, Info } from 'lucide-react';

interface EventTimelineProps {
  events: SimulationEvent[];
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events }) => {
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  const getEventBadge = (level: string) => {
    switch (level) {
      case 'SUCCESS':
        return {
          icon: CheckCircle2,
          color: 'text-emerald-400',
          bg: 'bg-emerald-950/40 border-emerald-500/30',
        };
      case 'WARNING':
        return {
          icon: AlertTriangle,
          color: 'text-amber-400',
          bg: 'bg-amber-950/40 border-amber-500/30',
        };
      case 'ERROR':
        return {
          icon: AlertOctagon,
          color: 'text-red-400',
          bg: 'bg-red-950/40 border-red-500/30',
        };
      default:
        return {
          icon: Info,
          color: 'text-cyan-400',
          bg: 'bg-cyan-950/40 border-cyan-500/30',
        };
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl overflow-hidden shadow-xl">
      <div className="flex items-center justify-between px-3.5 py-2.5 bg-slate-950/60 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Real-Time Coordination Event Stream
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-500">
          {events.length} EVENTS RECORDED
        </span>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-2.5 space-y-1.5 font-mono text-[11px] max-h-56"
      >
        {events.length === 0 ? (
          <div className="text-slate-500 text-center py-6 text-xs italic">
            Waiting for simulation start...
          </div>
        ) : (
          events.map((ev) => {
            const badge = getEventBadge(ev.level);
            const Icon = badge.icon;
            return (
              <div
                key={ev.id}
                className={`flex items-start space-x-2 p-1.5 rounded border transition-colors ${badge.bg}`}
              >
                <span className="text-slate-500 shrink-0 text-[10px]">
                  {ev.timestamp}
                </span>
                <Icon className={`w-3.5 h-3.5 shrink-0 mt-0.5 ${badge.color}`} />
                {ev.robot_id && (
                  <span className="px-1 py-0.2 rounded text-[9px] font-bold bg-slate-800 text-slate-200 shrink-0">
                    {ev.robot_id}
                  </span>
                )}
                <span className="text-slate-300 leading-tight break-words flex-1">
                  {ev.message}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
