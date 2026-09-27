import React, { useEffect } from 'react';
import type { SimulationState } from '../../types/warehouse';
import confetti from 'canvas-confetti';
import { Award, CheckCircle, X, RefreshCw, Layers } from 'lucide-react';

interface PerformanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  state: SimulationState | null;
  onRunAgain: () => void;
  onChangeScenario: () => void;
}

export const PerformanceModal: React.FC<PerformanceModalProps> = ({
  isOpen,
  onClose,
  state,
  onRunAgain,
  onChangeScenario,
}) => {
  useEffect(() => {
    if (isOpen && state?.all_completed) {
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
        });
      } catch (e) {
        // ignore
      }
    }
  }, [isOpen, state?.all_completed]);

  if (!isOpen || !state) return null;

  const m = state.metrics;
  const robots = state.robots;

  // Max values for bar charts
  const maxDist = Math.max(...robots.map((r) => r.distance), 1);
  const maxWait = Math.max(...robots.map((r) => r.waiting_ticks), 1);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden text-slate-200 font-mono">
        {/* Header banner */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-cyan-950/60 via-slate-900 to-purple-950/60 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-bold tracking-wider uppercase">
              DAA Autonomous Warehouse Performance Report
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
          {/* Status Badge */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/40">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-8 h-8 text-emerald-400 shrink-0" />
              <div>
                <h3 className="text-base font-bold text-emerald-300">
                  {state.all_completed ? 'SIMULATION MISSION COMPLETE' : 'LIVE BENCHMARK TELEMETRY'}
                </h3>
                <p className="text-xs text-emerald-500 font-sans mt-0.5">
                  ✓ {m.items_picked} / {m.total_items} items collected & delivered to packing stations
                </p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 block uppercase">Scenario</span>
              <span className="text-xs font-bold text-slate-200">{state.scenario_id}</span>
            </div>
          </div>

          {/* 6 Key Viva Metrics Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-500 block uppercase">Collisions</span>
              <span className="text-lg font-bold text-emerald-400">{m.collisions}</span>
              <span className="text-[10px] text-emerald-600 block">Strict zero safety guarantee</span>
            </div>

            <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-500 block uppercase">Deadlocks Detected</span>
              <span className="text-lg font-bold text-emerald-400">{m.deadlocks_detected}</span>
              <span className="text-[10px] text-emerald-600 block">
                {m.deadlocks_resolved} resolved via DFS cycle
              </span>
            </div>

            <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-500 block uppercase">Conflicts Resolved</span>
              <span className="text-lg font-bold text-amber-400">{m.conflicts_resolved}</span>
              <span className="text-[10px] text-slate-500 block">Greedy scheduler arbitration</span>
            </div>

            <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-500 block uppercase">Path Replans</span>
              <span className="text-lg font-bold text-purple-400">{m.path_replans}</span>
              <span className="text-[10px] text-slate-500 block">Dynamic A* reroutes</span>
            </div>

            <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-500 block uppercase">Total Distance</span>
              <span className="text-lg font-bold text-cyan-400">{m.total_distance_m} m</span>
              <span className="text-[10px] text-slate-500 block">Across 4 AGVs</span>
            </div>

            <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-500 block uppercase">Avg Planning Time</span>
              <span className="text-lg font-bold text-blue-400">{m.avg_planning_time_ms} ms</span>
              <span className="text-[10px] text-slate-500 block">A* heuristic efficiency</span>
            </div>
          </div>

          {/* Performance Comparison Bar Charts (Section 23) */}
          <div className="space-y-4 p-4 rounded-xl bg-slate-950/50 border border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Comparative Robot Workload Distribution
            </h4>

            {/* Distance Chart */}
            <div className="space-y-1.5">
              <span className="text-[10px] text-slate-400 block uppercase font-semibold">
                Robot Travel Distance (Meters):
              </span>
              {robots.map((r) => {
                const pct = (r.distance / maxDist) * 100;
                return (
                  <div key={r.id} className="flex items-center space-x-2 text-xs">
                    <span className="w-8 text-[11px] font-bold" style={{ color: r.color_hex }}>
                      {r.id}
                    </span>
                    <div className="flex-1 bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                      <div
                        className="h-full rounded-full transition-all duration-300"
                        style={{ width: `${pct}%`, backgroundColor: r.color_hex }}
                      />
                    </div>
                    <span className="w-16 text-right text-[11px] text-slate-300">
                      {r.distance.toFixed(1)} m
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Waiting Time Chart */}
            <div className="space-y-1.5 pt-2">
              <span className="text-[10px] text-slate-400 block uppercase font-semibold">
                Robot Aisle Waiting Ticks (Starvation Prevention):
              </span>
              {robots.map((r) => {
                const pct = (r.waiting_ticks / maxWait) * 100;
                return (
                  <div key={r.id} className="flex items-center space-x-2 text-xs">
                    <span className="w-8 text-[11px] font-bold" style={{ color: r.color_hex }}>
                      {r.id}
                    </span>
                    <div className="flex-1 bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                      <div
                        className="h-full rounded-full transition-all duration-300 bg-amber-400"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="w-16 text-right text-[11px] text-slate-300">
                      {r.waiting_ticks} ticks
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-end space-x-3 p-4 bg-slate-950/80 border-t border-slate-800">
          <button
            onClick={() => {
              onClose();
              onChangeScenario();
            }}
            className="flex items-center space-x-1.5 px-4 py-2 border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono transition-colors"
          >
            <Layers className="w-4 h-4" />
            <span>CHANGE SCENARIO</span>
          </button>
          <button
            onClick={() => {
              onClose();
              onRunAgain();
            }}
            className="flex items-center space-x-1.5 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold rounded-lg text-xs font-mono shadow-md shadow-cyan-950 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>RUN AGAIN</span>
          </button>
        </div>
      </div>
    </div>
  );
};
