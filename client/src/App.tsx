import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { EvalResults } from './pages/EvalResults';
import {
  fetchSummaryStats,
  fetchAgents,
  createAgent,
  buildBaseline,
  executeAndScoreTurn,
  fetchTimeline,
  fetchAttribution,
  runEvalSuite,
  fetchEvalRuns,
  SummaryStats,
  TimelinePoint,
  FeatureAttributionItem,
  EvalRunData,
  AgentData
} from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [agent, setAgent] = useState<AgentData | null>(null);
  const [stats, setStats] = useState<SummaryStats | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [attributions, setAttributions] = useState<FeatureAttributionItem[]>([]);
  const [evalRuns, setEvalRuns] = useState<EvalRunData[]>([]);

  const initSystem = async () => {
    try {
      // 1. Get or create agent
      const agents = await fetchAgents();
      let currentAgent: AgentData;
      if (agents.length > 0) {
        currentAgent = agents[0];
      } else {
        currentAgent = await createAgent(
          "Customer Support LangGraph Agent",
          "You are a helpful customer support and task automation AI agent."
        );
        // Automatically build initial baseline profile for new agent
        try {
          await buildBaseline(currentAgent.id, 20);
        } catch (e) {
          console.log("Auto-baseline build on init:", e);
        }
      }
      setAgent(currentAgent);

      // 2. Fetch stats, timeline, attribution
      refreshDashboardData(currentAgent.id);
    } catch (err) {
      console.error("Failed to initialize system:", err);
    }
  };

  const refreshDashboardData = async (agentId: string) => {
    try {
      const s = await fetchSummaryStats();
      setStats(s);

      const t = await fetchTimeline(agentId);
      setTimeline(t);

      const attr = await fetchAttribution(agentId);
      setAttributions(attr);

      const evs = await fetchEvalRuns(agentId);
      setEvalRuns(evs);
    } catch (err) {
      console.error("Error refreshing dashboard data:", err);
    }
  };

  useEffect(() => {
    initSystem();
    const interval = setInterval(() => {
      if (agent) refreshDashboardData(agent.id);
    }, 5000);
    return () => clearInterval(interval);
  }, [agent?.id]);

  const handleExecuteTurn = async (prompt: string) => {
    if (!agent) return;
    const result = await executeAndScoreTurn(agent.id, prompt);
    await refreshDashboardData(agent.id);
    return result;
  };

  const handleBuildBaseline = async () => {
    if (!agent) return;
    const result = await buildBaseline(agent.id, 20);
    await refreshDashboardData(agent.id);
    return result;
  };

  const handleRunEval = async () => {
    if (!agent) return;
    const result = await runEvalSuite(agent.id);
    await refreshDashboardData(agent.id);
    return result;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        agentName={agent?.name || 'Loading...'}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {activeTab === 'dashboard' ? (
          <Dashboard
            stats={stats}
            timeline={timeline}
            attributions={attributions}
            latestEval={evalRuns.length > 0 ? evalRuns[0] : null}
            agentId={agent?.id || ''}
            onExecuteTurn={handleExecuteTurn}
            onBuildBaseline={handleBuildBaseline}
            onRunEval={handleRunEval}
          />
        ) : (
          <EvalResults evalRuns={evalRuns} onRunEval={handleRunEval} />
        )}
      </main>
    </div>
  );
};
