import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SummaryStats {
  total_agents: number;
  total_turns_scored: number;
  total_flagged_turns: number;
  flag_rate: number;
  latest_precision: number;
  latest_recall: number;
  latest_fpr: number;
}

export interface TimelinePoint {
  id: string;
  turn_number: number;
  session_id: string;
  input_summary: string;
  isolation_score: number;
  mahalanobis_distance: number;
  combined_score: number;
  suspicion_accumulator: number;
  flagged: boolean;
  timestamp: string;
}

export interface FeatureAttributionItem {
  feature: string;
  avg_importance: number;
}

export interface AgentData {
  id: string;
  name: string;
  system_prompt: string;
  status: string;
  created_at: string;
}

export interface EvalRunData {
  id: string;
  agent_id: string;
  run_type: string;
  precision: number;
  recall: number;
  false_positive_rate: number;
  threshold_used: number;
  results: any;
  created_at: string;
}

export const fetchSummaryStats = async (): Promise<SummaryStats> => {
  const res = await apiClient.get('/dashboard/summary');
  return res.data;
};

export const fetchAgents = async (): Promise<AgentData[]> => {
  const res = await apiClient.get('/agents');
  return res.data;
};

export const createAgent = async (name: string, system_prompt: string): Promise<AgentData> => {
  const res = await apiClient.post('/agents', { name, system_prompt });
  return res.data;
};

export const buildBaseline = async (agent_id: string, scenario_count: number = 20) => {
  const res = await apiClient.post(`/agents/${agent_id}/baseline/build?scenario_count=${scenario_count}`);
  return res.data;
};

export const executeAndScoreTurn = async (agent_id: string, user_input: string): Promise<any> => {
  const res = await apiClient.post(`/agents/${agent_id}/execute_and_score?user_input=${encodeURIComponent(user_input)}`);
  return res.data;
};

export const fetchTimeline = async (agent_id: string): Promise<TimelinePoint[]> => {
  const res = await apiClient.get(`/dashboard/timeline/${agent_id}`);
  return res.data;
};

export const fetchAttribution = async (agent_id: string): Promise<FeatureAttributionItem[]> => {
  const res = await apiClient.get(`/dashboard/attribution/${agent_id}`);
  return res.data.top_features || [];
};

export const runEvalSuite = async (agent_id: string): Promise<EvalRunData> => {
  const res = await apiClient.post(`/eval/run/${agent_id}`);
  return res.data;
};

export const fetchEvalRuns = async (agent_id: string): Promise<EvalRunData[]> => {
  const res = await apiClient.get(`/eval/runs/${agent_id}`);
  return res.data;
};
