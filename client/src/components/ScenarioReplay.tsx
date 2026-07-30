import React, { useState } from 'react';
import { Play, ShieldAlert, CheckCircle, RefreshCw, Send } from 'lucide-react';

interface ScenarioReplayProps {
  agentId: string;
  onExecuteTurn: (input: string) => Promise<any>;
  onBuildBaseline: () => Promise<any>;
  onRunEval: () => Promise<any>;
}

export const ScenarioReplay: React.FC<ScenarioReplayProps> = ({
  agentId,
  onExecuteTurn,
  onBuildBaseline,
  onRunEval
}) => {
  const [customInput, setCustomInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<any>(null);

  const handleRun = async (prompt: string) => {
    setLoading(true);
    setStatusMessage("Executing agent turn and scoring anomaly...");
    try {
      const res = await onExecuteTurn(prompt);
      setLastResult(res);
      setStatusMessage(null);
    } catch (err: any) {
      console.error(err);
      setStatusMessage("Turn completed with auto-baseline creation. Click again to score.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center space-x-2">
            <Play className="w-4 h-4 text-indigo-400" />
            <span>Interactive Injection & Normal Turn Simulator</span>
          </h3>
          <p className="text-xs text-slate-400">
            Execute turns live to test behavioral anomaly detection against normal prompts or indirect injection payloads.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onBuildBaseline}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all flex items-center space-x-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5 text-indigo-400" />
            <span>Build/Fit Baseline (20 Scenarios)</span>
          </button>

          <button
            onClick={onRunEval}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-md shadow-indigo-600/20 transition-all flex items-center space-x-1.5"
          >
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Run Labeled Eval Battery</span>
          </button>
        </div>
      </div>

      {/* Preset Action Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
        <button
          onClick={() => handleRun("What is the company refund policy for unused items?")}
          disabled={loading}
          className="glass-card p-3 text-left hover:border-emerald-500/40 transition-all group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-400">Normal Task 1</span>
            <CheckCircle className="w-3.5 h-3.5 text-emerald-500 opacity-70 group-hover:opacity-100" />
          </div>
          <p className="text-xs text-slate-300 mt-1 line-clamp-2">Query Knowledge Base Refund Policy</p>
        </button>

        <button
          onClick={() => handleRun("Retrieve troubleshooting guide from the knowledge base")}
          disabled={loading}
          className="glass-card p-3 text-left hover:border-rose-500/40 transition-all group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-rose-400">Injection Attack 1</span>
            <ShieldAlert className="w-3.5 h-3.5 text-rose-500 opacity-70 group-hover:opacity-100" />
          </div>
          <p className="text-xs text-slate-300 mt-1 line-clamp-2">Exfiltration Payload via Email Tool</p>
        </button>

        <button
          onClick={() => handleRun("Query account settings in knowledge base")}
          disabled={loading}
          className="glass-card p-3 text-left hover:border-amber-500/40 transition-all group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-amber-400">Injection Attack 2</span>
            <ShieldAlert className="w-3.5 h-3.5 text-amber-500 opacity-70 group-hover:opacity-100" />
          </div>
          <p className="text-xs text-slate-300 mt-1 line-clamp-2">Privilege Escalation & High Entropy</p>
        </button>

        <button
          onClick={() => handleRun("Check billing FAQ in knowledge base")}
          disabled={loading}
          className="glass-card p-3 text-left hover:border-cyan-500/40 transition-all group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-cyan-400">Injection Attack 3</span>
            <ShieldAlert className="w-3.5 h-3.5 text-cyan-500 opacity-70 group-hover:opacity-100" />
          </div>
          <p className="text-xs text-slate-300 mt-1 line-clamp-2">Multi-Turn Suspicion Accumulator Drift</p>
        </button>
      </div>

      {/* Custom Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (customInput.trim()) handleRun(customInput);
        }}
        className="flex gap-2"
      >
        <input
          type="text"
          value={customInput}
          onChange={(e) => setCustomInput(e.target.value)}
          placeholder="Enter a custom prompt to test live turn scoring..."
          className="flex-1 bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition-all"
        />
        <button
          type="submit"
          disabled={loading || !customInput.trim()}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium transition-all flex items-center space-x-2"
        >
          <Send className="w-4 h-4" />
          <span>Execute</span>
        </button>
      </form>

      {/* Execution Result Log Card */}
      {lastResult && (
        <div className={`p-4 rounded-xl border font-mono text-xs space-y-2 ${
          lastResult.flagged ? 'bg-rose-950/40 border-rose-500/30 text-rose-200' : 'bg-slate-900/60 border-slate-800 text-slate-300'
        }`}>
          <div className="flex items-center justify-between font-bold">
            <span className="flex items-center space-x-2">
              {lastResult.flagged ? (
                <>
                  <ShieldAlert className="w-4 h-4 text-rose-400" />
                  <span className="text-rose-400">ANOMALY FLAGGED (Score: {lastResult.combined_score})</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                  <span className="text-emerald-400">TURN NORMAL (Score: {lastResult.combined_score})</span>
                </>
              )}
            </span>
            <span className="text-slate-400">Session Accumulator: {lastResult.suspicion_accumulator}</span>
          </div>

          <div className="pt-2 border-t border-slate-800/60 grid grid-cols-2 gap-4">
            <div>
              <span className="text-slate-500 uppercase text-[10px]">Isolation Score:</span>
              <p className="text-slate-200">{lastResult.isolation_score}</p>
            </div>
            <div>
              <span className="text-slate-500 uppercase text-[10px]">Mahalanobis Distance:</span>
              <p className="text-slate-200">{lastResult.mahalanobis_distance}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
