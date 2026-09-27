import React from 'react';
import { Play, Pause, StepForward, RotateCcw, Eye, Sparkles } from 'lucide-react';

interface SimulationControlsProps {
  isRunning: boolean;
  speed: number;
  onStart: () => void;
  onPause: () => void;
  onStep: () => void;
  onReset: () => void;
  onSetSpeed: (speed: number) => void;
  showAlgoOverlay: boolean;
  onToggleAlgoOverlay: () => void;
  onOpenPerformance: () => void;
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  isRunning,
  speed,
  onStart,
  onPause,
  onStep,
  onReset,
  onSetSpeed,
  showAlgoOverlay,
  onToggleAlgoOverlay,
  onOpenPerformance,
}) => {
  const speedOptions = [0.5, 1.0, 2.0, 4.0];

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl shadow-lg mb-4">
      {/* Primary Action Buttons */}
      <div className="flex items-center space-x-2">
        {isRunning ? (
          <button
            onClick={onPause}
            className="flex items-center space-x-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white font-semibold rounded-lg shadow-md shadow-amber-950/40 transition-all text-xs font-mono"
          >
            <Pause className="w-4 h-4" />
            <span>PAUSE</span>
          </button>
        ) : (
          <button
            onClick={onStart}
            className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg shadow-md shadow-emerald-950/40 transition-all text-xs font-mono"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>START</span>
          </button>
        )}

        <button
          onClick={onStep}
          disabled={isRunning}
          title="Single step tick (ideal for DAA algorithm trace presentation)"
          className={`flex items-center space-x-1.5 px-3 py-2 border rounded-lg text-xs font-mono transition-all ${
            isRunning
              ? 'opacity-40 cursor-not-allowed border-slate-800 text-slate-500'
              : 'border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200'
          }`}
        >
          <StepForward className="w-3.5 h-3.5" />
          <span>STEP</span>
        </button>

        <button
          onClick={onReset}
          className="flex items-center space-x-1.5 px-3 py-2 border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono transition-all"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>RESET</span>
        </button>
      </div>

      {/* Speed Controls */}
      <div className="flex items-center space-x-1.5 bg-slate-950/80 border border-slate-800 p-1 rounded-lg">
        <span className="text-[10px] font-mono text-slate-500 px-2 uppercase font-semibold">Speed:</span>
        {speedOptions.map((s) => (
          <button
            key={s}
            onClick={() => onSetSpeed(s)}
            className={`px-2.5 py-1 rounded text-xs font-mono font-medium transition-all ${
              speed === s
                ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            {s}x
          </button>
        ))}
      </div>

      {/* Algorithm Visual Overlay & Results Buttons */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onToggleAlgoOverlay}
          className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-mono border transition-all ${
            showAlgoOverlay
              ? 'bg-purple-950/60 border-purple-500 text-purple-300 shadow-sm shadow-purple-950'
              : 'border-slate-800 bg-slate-800/50 text-slate-400 hover:text-slate-200'
          }`}
        >
          <Eye className="w-3.5 h-3.5" />
          <span>ALGO TRACE: {showAlgoOverlay ? 'ON' : 'OFF'}</span>
        </button>

        <button
          onClick={onOpenPerformance}
          className="flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-mono border border-cyan-500/40 bg-cyan-950/30 text-cyan-300 hover:bg-cyan-900/40 transition-all"
        >
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>DAA REPORT</span>
        </button>
      </div>
    </div>
  );
};
