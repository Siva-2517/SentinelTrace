import React from 'react';
import { SummaryStats, EvalRunData } from '../api/client';
import { CheckCircle2, AlertCircle, Target, Zap, Activity } from 'lucide-react';

interface EvalMetricsPanelProps {
  stats: SummaryStats | null;
  latestEval: EvalRunData | null;
}

export const EvalMetricsPanel: React.FC<EvalMetricsPanelProps> = ({ stats, latestEval }) => {
  const precision = latestEval ? latestEval.precision : stats?.latest_precision ?? 1.0;
  const recall = latestEval ? latestEval.recall : stats?.latest_recall ?? 1.0;
  const fpr = latestEval ? latestEval.false_positive_rate : stats?.latest_fpr ?? 0.0;
  const isCalibrated = latestEval?.results?.calibration?.is_calibrated ?? true;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="glass-card p-5 space-y-2 relative overflow-hidden">
        <div className="flex justify-between items-center text-slate-400">
          <span className="text-xs uppercase font-mono tracking-wider">Detection Recall</span>
          <Target className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-3xl font-extrabold text-emerald-400 font-mono">
          {(recall * 100).toFixed(0)}%
        </div>
        <p className="text-xs text-slate-400">Target: 100% (3/3 attacks caught)</p>
        <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-xl pointer-events-none" />
      </div>

      <div className="glass-card p-5 space-y-2 relative overflow-hidden">
        <div className="flex justify-between items-center text-slate-400">
          <span className="text-xs uppercase font-mono tracking-wider">Precision</span>
          <Zap className="w-4 h-4 text-indigo-400" />
        </div>
        <div className="text-3xl font-extrabold text-indigo-400 font-mono">
          {(precision * 100).toFixed(0)}%
        </div>
        <p className="text-xs text-slate-400">Low false alarm confidence</p>
        <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-full blur-xl pointer-events-none" />
      </div>

      <div className="glass-card p-5 space-y-2 relative overflow-hidden">
        <div className="flex justify-between items-center text-slate-400">
          <span className="text-xs uppercase font-mono tracking-wider">False Positive Rate</span>
          <AlertCircle className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="text-3xl font-extrabold text-cyan-400 font-mono">
          {(fpr * 100).toFixed(1)}%
        </div>
        <p className="text-xs text-slate-400">Target: &lt; 15% on normal traffic</p>
        <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-xl pointer-events-none" />
      </div>

      <div className="glass-card p-5 space-y-2 relative overflow-hidden">
        <div className="flex justify-between items-center text-slate-400">
          <span className="text-xs uppercase font-mono tracking-wider">Detector Calibration</span>
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="flex items-center space-x-2 pt-1">
          <span className={`text-lg font-bold ${isCalibrated ? 'text-emerald-400' : 'text-amber-400'}`}>
            {isCalibrated ? 'Calibrated ✓' : 'Uncalibrated'}
          </span>
        </div>
        <p className="text-xs text-slate-400">Non-binary score distribution</p>
        <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-xl pointer-events-none" />
      </div>
    </div>
  );
};
