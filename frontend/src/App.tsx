import { useState, useEffect } from 'react';
import { useWarehouseSocket } from './hooks/useWarehouseSocket';
import type { RobotId } from './types/warehouse';
import { Header } from './components/Dashboard/Header';
import { TopStats } from './components/Simulation/TopStats';
import { SimulationControls } from './components/Simulation/SimulationControls';
import { ScenarioSelector } from './components/Simulation/ScenarioSelector';
import { WarehouseCanvas } from './components/Warehouse/WarehouseCanvas';
import { RobotCard } from './components/Robots/RobotCard';
import { EventTimeline } from './components/Simulation/EventTimeline';
import { AlgorithmPanel } from './components/Algorithms/AlgorithmPanel';
import { PerformanceModal } from './components/Dashboard/PerformanceModal';
import { Bot, Info } from 'lucide-react';

export function App() {
  const {
    state,
    isConnected,
    start,
    pause,
    step,
    reset,
    setSpeed,
    loadScenario,
  } = useWarehouseSocket();

  const [selectedRobotId, setSelectedRobotId] = useState<RobotId | null>(null);
  const [showAlgoOverlay, setShowAlgoOverlay] = useState<boolean>(true);
  const [showPerformanceModal, setShowPerformanceModal] = useState<boolean>(false);

  // Keyboard shortcut listener for slick presentation flow
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      if (e.code === 'Space') {
        e.preventDefault();
        if (state?.is_running) {
          pause();
        } else {
          start();
        }
      } else if (e.key === 's' || e.key === 'S') {
        step();
      } else if (e.key === 'r' || e.key === 'R') {
        reset();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [state?.is_running, start, pause, step, reset]);

  // Open celebration modal when all items delivered
  useEffect(() => {
    if (state?.all_completed) {
      setShowPerformanceModal(true);
    }
  }, [state?.all_completed]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-3 sm:p-5 font-sans selection:bg-cyan-500 selection:text-slate-950">
      <div className="max-w-[1720px] mx-auto space-y-4">
        {/* Header */}
        <Header
          isConnected={isConnected}
          onOpenReport={() => setShowPerformanceModal(true)}
        />

        {/* Top Telemetry Stats */}
        {state && (
          <TopStats
            metrics={state.metrics}
            robots={state.robots}
            isOnline={isConnected}
          />
        )}

        {/* Primary Simulation Controls */}
        {state && (
          <SimulationControls
            isRunning={state.is_running}
            speed={state.speed}
            onStart={start}
            onPause={pause}
            onStep={step}
            onReset={reset}
            onSetSpeed={setSpeed}
            showAlgoOverlay={showAlgoOverlay}
            onToggleAlgoOverlay={() => setShowAlgoOverlay(!showAlgoOverlay)}
            onOpenPerformance={() => setShowPerformanceModal(true)}
          />
        )}

        {/* Scenario Selection Cards */}
        {state && (
          <ScenarioSelector
            currentScenarioId={state.scenario_id}
            onSelectScenario={loadScenario}
          />
        )}

        {/* Main Operational Simulation Stage */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
          {/* Warehouse Canvas (Columns 1-3 on XL screens) */}
          <div className="xl:col-span-3 h-[600px] xl:h-[660px] flex flex-col">
            <div className="flex-1 rounded-xl overflow-hidden shadow-2xl relative">
              <WarehouseCanvas
                state={state}
                selectedRobotId={selectedRobotId}
                onSelectRobot={setSelectedRobotId}
                showAlgoOverlay={showAlgoOverlay}
                activeAlgoTab="ASTAR"
              />
            </div>
          </div>

          {/* 4 Robot Telemetry Cards (Column 4) */}
          <div className="flex flex-col space-y-3">
            <div className="flex items-center justify-between px-1 text-xs font-mono text-slate-400">
              <div className="flex items-center space-x-1.5">
                <Bot className="w-4 h-4 text-cyan-400" />
                <span className="font-bold uppercase tracking-wider text-slate-200">
                  AGV Fleet Telemetry
                </span>
              </div>
              <span className="text-[10px] text-slate-500">CLICK TO FOCUS</span>
            </div>

            {state?.robots.map((robot) => (
              <RobotCard
                key={robot.id}
                robot={robot}
                isSelected={selectedRobotId === robot.id}
                onSelect={(id) => setSelectedRobotId(selectedRobotId === id ? null : id)}
              />
            ))}

            {/* Quick DAA Presentation Hint Card */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 font-mono space-y-1">
              <div className="flex items-center space-x-1.5 text-cyan-400 font-bold">
                <Info className="w-3.5 h-3.5" />
                <span>DAA Presentation Tip</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-relaxed font-sans">
                Select <span className="text-cyan-300 font-mono">Scenario 3</span> (4-Way Conflict), click{' '}
                <span className="text-emerald-400 font-mono">START</span> or press{' '}
                <kbd className="px-1 py-0.5 bg-slate-800 rounded text-slate-200">SPACE</kbd> to watch greedy arbitration and dynamic A* replanning live!
              </p>
            </div>
          </div>
        </div>

        {/* Lower Row: Event Timeline & DAA Algorithm Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-1">
          {/* Live Coordination Event Timeline */}
          <EventTimeline events={state?.recent_events || []} />

          {/* DAA Algorithm Engine Inspector */}
          <AlgorithmPanel state={state} selectedRobotId={selectedRobotId} />
        </div>
      </div>

      {/* DAA Viva Performance Benchmark Modal */}
      <PerformanceModal
        isOpen={showPerformanceModal}
        onClose={() => setShowPerformanceModal(false)}
        state={state}
        onRunAgain={reset}
        onChangeScenario={() => window.scrollTo({ top: 180, behavior: 'smooth' })}
      />
    </div>
  );
}

export default App;
