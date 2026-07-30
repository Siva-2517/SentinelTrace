import React from 'react';
import { SummaryStats, TimelinePoint, FeatureAttributionItem, EvalRunData } from '../api/client';
import { EvalMetricsPanel } from '../components/EvalMetricsPanel';
import { AnomalyTimeline } from '../components/AnomalyTimeline';
import { FeatureAttribution } from '../components/FeatureAttribution';
import { ScenarioReplay } from '../components/ScenarioReplay';

interface DashboardProps {
  stats: SummaryStats | null;
  timeline: TimelinePoint[];
  attributions: FeatureAttributionItem[];
  latestEval: EvalRunData | null;
  agentId: string;
  onExecuteTurn: (input: string) => Promise<any>;
  onBuildBaseline: () => Promise<any>;
  onRunEval: () => Promise<any>;
}

export const Dashboard: React.FC<DashboardProps> = ({
  stats,
  timeline,
  attributions,
  latestEval,
  agentId,
  onExecuteTurn,
  onBuildBaseline,
  onRunEval
}) => {
  return (
    <div className="space-y-6">
      <EvalMetricsPanel stats={stats} latestEval={latestEval} />

      <ScenarioReplay
        agentId={agentId}
        onExecuteTurn={onExecuteTurn}
        onBuildBaseline={onBuildBaseline}
        onRunEval={onRunEval}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AnomalyTimeline timeline={timeline} />
        </div>

        <div>
          <FeatureAttribution attributions={attributions} />
        </div>
      </div>
    </div>
  );
};
