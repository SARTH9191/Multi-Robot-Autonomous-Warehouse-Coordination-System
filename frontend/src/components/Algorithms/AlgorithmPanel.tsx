import React, { useState } from 'react';
import type { SimulationState, RobotId } from '../../types/warehouse';
import { Cpu } from 'lucide-react';

interface AlgorithmPanelProps {
  state: SimulationState | null;
  selectedRobotId: RobotId | null;
}

export const AlgorithmPanel: React.FC<AlgorithmPanelProps> = ({ state, selectedRobotId }) => {
  const [activeTab, setActiveTab] = useState<'ASTAR' | 'DP' | 'GEOMETRY' | 'SCHEDULER'>('ASTAR');

  const activeRobot = selectedRobotId || 'R1';
  const astarSample = state?.last_astar?.[activeRobot];
  const dpSample = state?.last_dp?.[activeRobot];

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl p-4 shadow-xl">
      {/* Header with DAA Viva Badges */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            DAA Core Algorithms Engine
          </h3>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs font-mono">
          <button
            onClick={() => setActiveTab('ASTAR')}
            className={`px-2.5 py-1 rounded transition-colors ${
              activeTab === 'ASTAR'
                ? 'bg-blue-600 text-white font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            A* Search
          </button>
          <button
            onClick={() => setActiveTab('DP')}
            className={`px-2.5 py-1 rounded transition-colors ${
              activeTab === 'DP'
                ? 'bg-purple-600 text-white font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            DP-TSP
          </button>
          <button
            onClick={() => setActiveTab('GEOMETRY')}
            className={`px-2.5 py-1 rounded transition-colors ${
              activeTab === 'GEOMETRY'
                ? 'bg-amber-600 text-white font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Geometry
          </button>
          <button
            onClick={() => setActiveTab('SCHEDULER')}
            className={`px-2.5 py-1 rounded transition-colors ${
              activeTab === 'SCHEDULER'
                ? 'bg-emerald-600 text-white font-bold shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Greedy Scheduler
          </button>
        </div>
      </div>

      {/* Content for Active Tab */}
      {activeTab === 'ASTAR' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Inspected AGV</span>
              <span className="text-cyan-400 font-bold">{activeRobot}</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Heuristic Form</span>
              <span className="text-slate-200 font-bold">f(n) = g(n) + h(n)</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Nodes Explored</span>
              <span className="text-purple-400 font-bold">
                {astarSample ? astarSample.nodes_explored : 0} nodes
              </span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Planning Runtime</span>
              <span className="text-emerald-400 font-bold">
                {astarSample ? `${astarSample.execution_time_ms} ms` : '0.0 ms'}
              </span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/80 text-[11px] text-slate-300">
            <span className="font-bold text-blue-400 uppercase tracking-wider block mb-1">
              Time-Space Heuristic Mechanics:
            </span>
            <span>
              Calculates 4-connected grid path with Manhattan metric{' '}
              <code className="bg-slate-800 px-1 py-0.5 rounded text-amber-300">
                h(a,b) = |x1-x2| + |y1-y2|
              </code>
              . Incorporates dynamic obstacles and reservation tables to preemptively prevent vertex & edge collisions.
            </span>
          </div>
        </div>
      )}

      {activeTab === 'DP' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Subproblem Recurrence</span>
              <span className="text-purple-400 font-bold">DP[mask][i]</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">States Calculated</span>
              <span className="text-cyan-400 font-bold">
                {dpSample ? dpSample.dp_states_calculated : 0} states
              </span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Distance Saved</span>
              <span className="text-emerald-400 font-bold">
                {dpSample ? `${dpSample.saved_distance} cells` : '0 cells'}
              </span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Execution Runtime</span>
              <span className="text-amber-400 font-bold">
                {dpSample ? `${dpSample.execution_time_ms} ms` : '0.0 ms'}
              </span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/80 text-[11px] text-slate-300">
            <span className="font-bold text-purple-400 uppercase tracking-wider block mb-1">
              Held-Karp Bitmask Permutation Formulation:
            </span>
            <div className="text-slate-400 mb-1">
              For subset mask <code className="text-amber-300 font-mono">S</code> ending at shelf{' '}
              <code className="text-amber-300 font-mono">i</code>:
            </div>
            <div className="bg-slate-900 p-2 rounded border border-slate-800 font-mono text-[10px] text-cyan-300 overflow-x-auto">
              DP[mask][i] = min_{`{j ∈ mask \\ {i}}`} (DP[mask ^ (1 &lt;&lt; i)][j] + dist(j, i))
            </div>
          </div>
        </div>
      )}

      {activeTab === 'GEOMETRY' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Orientation Function</span>
              <span className="text-amber-400 font-bold">orientation(p,q,r)</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Intersection Test</span>
              <span className="text-cyan-400 font-bold">segmentsIntersect(A,B,C,D)</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Safety Radius</span>
              <span className="text-emerald-400 font-bold">1.25 meters</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Active Warnings</span>
              <span className="text-red-400 font-bold">
                {state?.proximities?.length || 0} active
              </span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/80 text-[11px] text-slate-300">
            <span className="font-bold text-amber-400 uppercase tracking-wider block mb-1">
              Cross Product Orientation Determinant:
            </span>
            <div className="bg-slate-900 p-2 rounded border border-slate-800 font-mono text-[10px] text-amber-300">
              val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
            </div>
            <span className="block mt-1 text-slate-400">
              val == 0 (Collinear) | val &gt; 0 (Clockwise) | val &lt; 0 (Counterclockwise).
            </span>
          </div>
        </div>
      )}

      {activeTab === 'SCHEDULER' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Greedy Priority Formula</span>
              <span className="text-emerald-400 font-bold">urgency + wait - dist</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Conflicts Resolved</span>
              <span className="text-cyan-400 font-bold">
                {state?.metrics?.conflicts_resolved || 0}
              </span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Deadlock Graph</span>
              <span className="text-purple-400 font-bold">DFS 3-Color Cycle</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Starvation Prevention</span>
              <span className="text-amber-400 font-bold">Wait Factor: 2.5x</span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/80 text-[11px] text-slate-300">
            <span className="font-bold text-emerald-400 uppercase tracking-wider block mb-1">
              Arbitration Strategy & Deadlock Prevention:
            </span>
            <span>
              Intersection priority builds a dynamic wait-queue. If circular dependencies occur (R1 waits for R2, R2 waits for R3, R3 waits for R1), DFS cycle detection identifies the lowest-priority AGV to yield into a side pocket and recalculate its path via A*.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
