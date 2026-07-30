import React from 'react';
import { EvalRunData } from '../api/client';
import { Award, CheckCircle2, XCircle, ShieldCheck } from 'lucide-react';

interface EvalResultsProps {
  evalRuns: EvalRunData[];
  onRunEval: () => Promise<any>;
}

export const EvalResults: React.FC<EvalResultsProps> = ({ evalRuns, onRunEval }) => {
  const latestRun = evalRuns.length > 0 ? evalRuns[0] : null;

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <Award className="w-6 h-6 text-indigo-400" />
            <span>Evaluation & ROC Calibration Benchmark Suite</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Persisted evaluation benchmarks measuring recall on indirect injection attacks and precision on normal agent traffic.
          </p>
        </div>

        <button
          onClick={onRunEval}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-600/25"
        >
          Run Full Evaluation Harness
        </button>
      </div>

      {latestRun && (
        <div className="glass-panel p-6 space-y-4">
          <h3 className="text-base font-semibold text-slate-200">Latest Run Detailed Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card p-4">
              <span className="text-xs text-slate-400 font-mono">Precision</span>
              <p className="text-2xl font-bold text-indigo-400 font-mono">{(latestRun.precision * 100).toFixed(1)}%</p>
            </div>

            <div className="glass-card p-4">
              <span className="text-xs text-slate-400 font-mono">Recall</span>
              <p className="text-2xl font-bold text-emerald-400 font-mono">{(latestRun.recall * 100).toFixed(1)}%</p>
            </div>

            <div className="glass-card p-4">
              <span className="text-xs text-slate-400 font-mono">False Positive Rate</span>
              <p className="text-2xl font-bold text-cyan-400 font-mono">{(latestRun.false_positive_rate * 100).toFixed(1)}%</p>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h4 className="text-sm font-semibold text-slate-300 mb-3">Scenario Breakdown</h4>
            <div className="space-y-2">
              {latestRun.results?.results?.map((item: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
                  <div className="flex items-center space-x-3">
                    {item.passed ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-400" />
                    )}
                    <span className="font-mono text-slate-300">{item.scenario_id}</span>
                    <span className="text-slate-400 truncate max-w-md">{item.prompt}</span>
                  </div>
                  <div className="flex items-center space-x-4 font-mono">
                    <span className="text-slate-400">Score: {item.score}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] ${item.label === 1 ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                      {item.label === 1 ? 'INJECTED' : 'NORMAL'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
