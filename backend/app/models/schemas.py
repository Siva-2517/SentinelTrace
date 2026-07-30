from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Agent Schemas
class AgentBase(BaseModel):
    name: str = Field(..., example="Customer Support LangGraph Agent")
    system_prompt: str = Field(..., example="You are a helpful customer support agent...")
    tool_manifest: List[Dict[str, Any]] = Field(default_factory=list)


class AgentCreate(AgentBase):
    pass


class AgentResponse(AgentBase):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Turn Event Schemas
class ToolCallRecord(BaseModel):
    tool: str
    params: Dict[str, Any] = Field(default_factory=dict)
    response_length: int = 0
    latency_ms: float = 0.0


class AgentTurnIngest(BaseModel):
    session_id: str
    turn_number: int
    input_summary: Optional[str] = None
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    output_summary: Optional[str] = None
    is_synthetic: bool = False


class AgentTurnResponse(AgentTurnIngest):
    id: str
    agent_id: str
    feature_vector: Optional[List[float]] = None
    timestamp: datetime

    class Config:
        from_attributes = True


# Anomaly Scoring Schemas
class ScoreResponse(BaseModel):
    id: str
    turn_event_id: str
    isolation_score: float
    mahalanobis_distance: float
    combined_score: float
    suspicion_accumulator: float
    flagged: bool
    feature_attribution: Dict[str, float]
    created_at: datetime

    class Config:
        from_attributes = True


# Baseline Schemas
class BaselineProfileResponse(BaseModel):
    id: str
    agent_id: str
    feature_means: List[float]
    feature_covariance: List[List[float]]
    scenario_count: int
    version: int
    created_at: datetime

    class Config:
        from_attributes = True


# Eval Schemas
class EvalRunResponse(BaseModel):
    id: str
    agent_id: str
    run_type: str
    precision: float
    recall: float
    false_positive_rate: float
    threshold_used: float
    results: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
