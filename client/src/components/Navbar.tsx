import React from 'react';
import { Shield, Cpu, Activity, BarChart2, CheckCircle2 } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  agentName: string;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, agentName }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-300">
              SentinelTrace
            </h1>
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">
              v1.0.0
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono">Behavioral Anomaly Detector for Indirect Injection</p>
        </div>
      </div>

      <nav className="flex items-center space-x-2 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'dashboard'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <Activity className="w-4 h-4" />
          <span>Live Timeline</span>
        </button>

        <button
          onClick={() => setActiveTab('eval')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'eval'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          <span>Evaluation Metrics</span>
        </button>
      </nav>

      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Agent Monitored: {agentName || 'LangGraph Agent'}</span>
        </div>
      </div>
    </header>
  );
};
