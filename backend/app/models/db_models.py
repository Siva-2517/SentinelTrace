import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import (
    Column, String, Text, Float, Boolean, Integer, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    system_prompt = Column(Text, nullable=False)
    tool_manifest = Column(JSON, nullable=False, default=list)
    status = Column(String(30), default="active")  # active, baselining, suspended
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    baselines = relationship("BaselineProfile", back_populates="agent", cascade="all, delete-orphan")
    turn_events = relationship("AgentTurnEvent", back_populates="agent", cascade="all, delete-orphan")
    eval_runs = relationship("EvalRun", back_populates="agent", cascade="all, delete-orphan")


class BaselineProfile(Base):
    __tablename__ = "baseline_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    feature_means = Column(JSON, nullable=False)
    feature_covariance = Column(JSON, nullable=False)
    isolation_forest_serialized = Column(Text, nullable=False)  # Base64 serialized model
    scenario_count = Column(Integer, default=20)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="baselines")


class AgentTurnEvent(Base):
    __tablename__ = "agent_turn_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False)
    input_summary = Column(Text, nullable=True)
    tool_calls = Column(JSON, nullable=False, default=list)  # [{tool, params, response_length, latency_ms}]
    output_summary = Column(Text, nullable=True)
    feature_vector = Column(JSON, nullable=True)
    is_synthetic = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    agent = relationship("Agent", back_populates="turn_events")
    anomaly_score = relationship("AnomalyScore", uselist=False, back_populates="turn_event", cascade="all, delete-orphan")


class AnomalyScore(Base):
    __tablename__ = "anomaly_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    turn_event_id = Column(String(36), ForeignKey("agent_turn_events.id"), nullable=False, unique=True)
    isolation_score = Column(Float, nullable=False)
    mahalanobis_distance = Column(Float, nullable=False)
    combined_score = Column(Float, nullable=False)
    suspicion_accumulator = Column(Float, nullable=False, default=0.0)
    flagged = Column(Boolean, default=False)
    feature_attribution = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    turn_event = relationship("AgentTurnEvent", back_populates="anomaly_score")


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    run_type = Column(String(50), nullable=False)  # baseline_regression, injection_test, redteam
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    false_positive_rate = Column(Float, nullable=False)
    threshold_used = Column(Float, nullable=False)
    results = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="eval_runs")


class InjectionPayload(Base):
    __tablename__ = "injection_payloads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    payload_content = Column(Text, nullable=False)
    injection_vector = Column(String(50), nullable=False)  # tool_output, retrieved_doc, api_response
    expected_deviation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
