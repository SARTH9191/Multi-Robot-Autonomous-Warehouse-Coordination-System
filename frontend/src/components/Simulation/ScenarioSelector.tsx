import React from 'react';
import { Layers, AlertOctagon, GitMerge, ShieldAlert, Cpu, Sparkles } from 'lucide-react';

interface ScenarioSelectorProps {
  currentScenarioId: string;
  onSelectScenario: (id: string) => void;
}

export const ScenarioSelector: React.FC<ScenarioSelectorProps> = ({
  currentScenarioId,
  onSelectScenario,
}) => {
  const scenarios = [
    {
      id: 'SCENARIO_1',
      title: 'Scenario 1: Normal Operation',
      badge: 'Standard Flow',
      icon: Layers,
      color: 'text-blue-400',
      desc: 'Conflict-free baseline. Demonstrates clean multi-robot routing across 4 quadrants.',
    },
    {
      id: 'SCENARIO_2',
      title: 'Scenario 2: Intersection Conflict',
      badge: '2-Way Hazard',
      icon: GitMerge,
      color: 'text-amber-400',
      desc: 'R1 and R2 converge simultaneously at central intersection (15, 11). Greedy scheduler calculates priority.',
    },
    {
      id: 'SCENARIO_3',
      title: 'Scenario 3: Four Robot Conflict',
      badge: '4-Way Convergence',
      icon: AlertOctagon,
      color: 'text-red-400',
      desc: 'Key DAA Demo: All 4 AGVs converge on the central aisle corridor. Demonstrates queuing & priority arbitration.',
    },
    {
      id: 'SCENARIO_4',
      title: 'Scenario 4: Dynamic Obstacle',
      badge: 'Dynamic Replanning',
      icon: ShieldAlert,
      color: 'text-purple-400',
      desc: 'Simulated aisle spill blocks northern corridor. Tests live A* dynamic detour recalculation.',
    },
    {
      id: 'SCENARIO_5',
      title: 'Scenario 5: Deadlock Yield Test',
      badge: 'Cycle Resolution',
      icon: Cpu,
      color: 'text-rose-400',
      desc: 'Robots meet in narrow single-lane aisle. DFS cycle detection identifies wait-for deadlock and triggers yield.',
    },
    {
      id: 'SCENARIO_6',
      title: 'Scenario 6: Stress Test',
      badge: 'Heavy Workload (16 items)',
      icon: Sparkles,
      color: 'text-cyan-400',
      desc: 'Full warehouse capacity: 16 items distributed across all racks with intense corridor traffic.',
    },
  ];

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            DAA Demonstration Scenarios
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-500">
          SELECT TO RUN BENCHMARK
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
        {scenarios.map((sc) => {
          const Icon = sc.icon;
          const isSelected = currentScenarioId === sc.id;
          return (
            <div
              key={sc.id}
              onClick={() => onSelectScenario(sc.id)}
              className={`p-3 rounded-lg border transition-all cursor-pointer select-none ${
                isSelected
                  ? 'border-cyan-500/80 bg-cyan-950/20 shadow-md shadow-cyan-950/40 ring-1 ring-cyan-500/50'
                  : 'border-slate-800/80 bg-slate-950/40 hover:border-slate-700 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center space-x-2">
                  <Icon className={`w-3.5 h-3.5 ${sc.color}`} />
                  <span className="text-xs font-mono font-bold text-slate-200 truncate">
                    {sc.title}
                  </span>
                </div>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  {sc.badge}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug line-clamp-2">
                {sc.desc}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
