from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.db_models import Agent, BaselineProfile, AgentTurnEvent, AnomalyScore
from app.models.schemas import AgentTurnIngest, ScoreResponse
from app.agent.sample_agent import sample_agent_instance
from app.ml.feature_extraction import extract_turn_features
from app.ml.anomaly_scorer import anomaly_scorer_instance
from app.ml.suspicion_accumulator import suspicion_accumulator_instance
from app.services.baseline_service import build_baseline_profile

router = APIRouter(prefix="/agents/{agent_id}", tags=["Scoring & Ingestion"])


@router.post("/turns", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
async def ingest_and_score_turn(agent_id: str, turn_in: AgentTurnIngest, db: AsyncSession = Depends(get_db)):
    """Ingest an agent turn event, extract features, score against baseline, and update session suspicion score."""
    # 1. Fetch latest baseline profile; auto-build if not yet created
    res_b = await db.execute(
        select(BaselineProfile)
        .where(BaselineProfile.agent_id == agent_id)
        .order_by(BaselineProfile.version.desc())
    )
    baseline = res_b.scalars().first()
    if not baseline:
        # Auto-build initial baseline profile for seamless execution
        try:
            baseline = await build_baseline_profile(agent_id, 20, db)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Agent has no baseline and auto-build failed: {str(e)}"
            )

    tool_calls_list = [tc.model_dump() for tc in turn_in.tool_calls]
    fv = extract_turn_features(tool_calls_list)

    # 2. Store AgentTurnEvent
    turn_event = AgentTurnEvent(
        agent_id=agent_id,
        session_id=turn_in.session_id,
        turn_number=turn_in.turn_number,
        input_summary=turn_in.input_summary,
        tool_calls=tool_calls_list,
        output_summary=turn_in.output_summary,
        feature_vector=fv,
        is_synthetic=turn_in.is_synthetic
    )
    db.add(turn_event)
    await db.flush()

    # 3. Score turn
    score_dict = anomaly_scorer_instance.score_turn(
        fv,
        baseline.feature_means,
        baseline.feature_covariance,
        baseline.isolation_forest_serialized
    )

    # 4. Fetch previous turn suspicion accumulator for session
    res_s = await db.execute(
        select(AnomalyScore)
        .join(AgentTurnEvent)
        .where(AgentTurnEvent.agent_id == agent_id, AgentTurnEvent.session_id == turn_in.session_id)
        .order_by(AgentTurnEvent.turn_number.desc())
    )
    prev_score = res_s.scalars().first()
    prev_accumulator = prev_score.suspicion_accumulator if prev_score else 0.0

    current_accumulator = suspicion_accumulator_instance.calculate_next_score(
        prev_accumulator, score_dict["combined_score"]
    )

    # Flag session if accumulator or combined score exceeds threshold
    flagged = score_dict["flagged"] or (current_accumulator >= 1.5)

    anomaly_score = AnomalyScore(
        turn_event_id=turn_event.id,
        isolation_score=score_dict["isolation_score"],
        mahalanobis_distance=score_dict["mahalanobis_distance"],
        combined_score=score_dict["combined_score"],
        suspicion_accumulator=current_accumulator,
        flagged=flagged,
        feature_attribution=score_dict["feature_attribution"]
    )
    db.add(anomaly_score)
    await db.commit()
    await db.refresh(anomaly_score)
    return anomaly_score


@router.post("/execute_and_score", response_model=ScoreResponse)
async def execute_and_score_turn(
    agent_id: str,
    user_input: str,
    session_id: str = "demo_session",
    turn_number: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Executes sample agent on user input and immediately scores the resulting turn."""
    turn_res = await sample_agent_instance.execute_turn(user_input)

    turn_in = AgentTurnIngest(
        session_id=session_id,
        turn_number=turn_number,
        input_summary=user_input,
        tool_calls=turn_res["tool_calls"],
        output_summary=turn_res["output_summary"],
        is_synthetic=False
    )
    return await ingest_and_score_turn(agent_id, turn_in, db)
