import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { TimelinePoint } from '../api/client';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

interface AnomalyTimelineProps {
  timeline: TimelinePoint[];
}

export const AnomalyTimeline: React.FC<AnomalyTimelineProps> = ({ timeline }) => {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="glass-panel p-8 text-center text-slate-400">
        <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto mb-3 animate-pulse" />
        <p className="font-medium">No turn scoring events recorded yet.</p>
        <p className="text-sm text-slate-500 mt-1">Run synthetic scenarios or execute turn actions below to trigger scoring.</p>
      </div>
    );
  }

  const chartData = timeline.map((pt) => ({
    name: `Turn ${pt.turn_number}`,
    CombinedScore: pt.combined_score,
    SuspicionAccumulator: pt.suspicion_accumulator,
    IsolationScore: pt.isolation_score,
    MahalanobisDist: Math.min(1.0, pt.mahalanobis_distance / 10.0),
    flagged: pt.flagged,
    input: pt.input_summary
  }));

  const flaggedCount = timeline.filter((t) => t.flagged).length;

  return (
    <div className="glass-panel p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <span>Real-Time Turn Anomaly Scoring Timeline</span>
            {flaggedCount > 0 && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center space-x-1">
                <AlertTriangle className="w-3 h-3 inline" />
                <span>{flaggedCount} Anomaly Flags</span>
              </span>
            )}
          </h2>
          <p className="text-xs text-slate-400">
            Measures turn-level Isolation Forest score, Mahalanobis distance, and cross-turn suspicion accumulator.
          </p>
        </div>
      </div>

      <div className="h-80 w-full pt-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 1.2]} stroke="#64748b" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '8px',
                color: '#f8fafc'
              }}
            />
            <Legend wrapperStyle={{ paddingTop: '10px' }} />
            <ReferenceLine y={0.65} label={{ value: 'Anomaly Threshold (0.65)', fill: '#f43f5e', fontSize: 11 }} stroke="#f43f5e" strokeDasharray="5 5" />
            <Line type="monotone" dataKey="CombinedScore" stroke="#818cf8" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 7 }} />
            <Line type="monotone" dataKey="SuspicionAccumulator" stroke="#f43f5e" strokeWidth={2} strokeDasharray="3 3" dot={{ r: 3 }} />
            <Line type="monotone" dataKey="IsolationScore" stroke="#06b6d4" strokeWidth={1.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
