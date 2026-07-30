import React from 'react';
import { FeatureAttributionItem } from '../api/client';
import { Layers } from 'lucide-react';

interface FeatureAttributionProps {
  attributions: FeatureAttributionItem[];
}

export const FeatureAttribution: React.FC<FeatureAttributionProps> = ({ attributions }) => {
  return (
    <div className="glass-panel p-6 space-y-4">
      <div className="flex items-center space-x-2">
        <Layers className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-semibold text-slate-100">Explainable Feature Attribution</h3>
      </div>
      <p className="text-xs text-slate-400">
        Relative weight of each feature signal driving the anomaly score calculation.
      </p>

      {attributions.length === 0 ? (
        <p className="text-xs text-slate-500 italic py-4">No feature attribution data collected yet.</p>
      ) : (
        <div className="space-y-3 pt-2">
          {attributions.slice(0, 6).map((item, idx) => {
            const pct = Math.min(100, Math.round(item.avg_importance * 100));
            return (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-300">{item.feature}</span>
                  <span className="text-indigo-400 font-semibold">{pct}%</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full transition-all duration-500"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
