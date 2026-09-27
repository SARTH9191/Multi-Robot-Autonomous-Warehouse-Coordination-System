import React from 'react';
import { Warehouse, Wifi, WifiOff, Sparkles } from 'lucide-react';

interface HeaderProps {
  isConnected: boolean;
  onOpenReport: () => void;
}

export const Header: React.FC<HeaderProps> = ({ isConnected, onOpenReport }) => {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 p-4 mb-4 bg-slate-900/90 backdrop-blur-md border border-slate-800 rounded-2xl shadow-xl">
      <div className="flex items-center space-x-3.5">
        <div className="p-2.5 bg-cyan-950/60 border border-cyan-500/30 rounded-xl shadow-inner shadow-cyan-900/50">
          <Warehouse className="w-6 h-6 text-cyan-400" />
        </div>
        <div>
          <h1 className="text-base sm:text-lg font-black tracking-wide text-white flex items-center gap-2">
            AUTONOMOUS WAREHOUSE CONTROL CENTER
            <span className="hidden sm:inline-block px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950 text-cyan-400 border border-cyan-500/30 uppercase tracking-widest">
              DAA AGV Fleet
            </span>
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Multi-Robot Coordination System • A* • DP-TSP • Computational Geometry • Greedy Scheduler
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Connection Pulse */}
        <div
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full border text-xs font-mono ${
            isConnected
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
              : 'bg-red-950/40 border-red-500/40 text-red-300'
          }`}
        >
          {isConnected ? (
            <>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <Wifi className="w-3.5 h-3.5 ml-1" />
              <span>LIVE SERVER</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3.5 h-3.5" />
              <span>CONNECTING...</span>
            </>
          )}
        </div>

        {/* DAA Report Action */}
        <button
          onClick={onOpenReport}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono transition-all"
        >
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>VIVA REPORT</span>
        </button>
      </div>
    </header>
  );
};
