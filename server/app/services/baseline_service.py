from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.db_models import Agent, BaselineProfile, AgentTurnEvent
from app.agent.sample_agent import sample_agent_instance
from app.ml.feature_extraction import extract_turn_features
from app.ml.baseline_profiler import BaselineProfiler
from app.simulation.scenario_generator import generate_synthetic_scenarios


async def build_baseline_profile(agent_id: str, scenario_count: int, db: Session) -> BaselineProfile:
    """Helper service function to generate synthetic scenarios and fit baseline profile."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise ValueError(f"Agent with ID {agent_id} not found")

    scenarios = generate_synthetic_scenarios(scenario_count)
    feature_matrix = []

    # Execute synthetic scenarios and store turn events
    for idx, prompt in enumerate(scenarios):
        turn_res = await sample_agent_instance.execute_turn(prompt)
        tool_calls_dict = turn_res["tool_calls"]
        fv = extract_turn_features(tool_calls_dict)
        feature_matrix.append(fv)

        turn_event = AgentTurnEvent(
            agent_id=agent_id,
            session_id="synthetic_baseline_session",
            turn_number=idx + 1,
            input_summary=prompt,
            tool_calls=tool_calls_dict,
            output_summary=turn_res["output_summary"],
            feature_vector=fv,
            is_synthetic=True
        )
        db.add(turn_event)

    # Fit baseline model parameters
    profiler = BaselineProfiler()
    means, cov, iso_serialized = profiler.fit_baseline(feature_matrix)

    latest = db.query(BaselineProfile).filter(BaselineProfile.agent_id == agent_id).order_by(BaselineProfile.version.desc()).first()
    next_version = (latest.version + 1) if latest else 1

    baseline = BaselineProfile(
        agent_id=agent_id,
        feature_means=means,
        feature_covariance=cov,
        isolation_forest_serialized=iso_serialized,
        scenario_count=scenario_count,
        version=next_version
    )
    db.add(baseline)
    agent.status = "active"
    db.commit()
    db.refresh(baseline)
    return baseline
