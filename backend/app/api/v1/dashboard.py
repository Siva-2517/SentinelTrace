from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.db.session import get_db
from app.models.db_models import Agent, AgentTurnEvent, AnomalyScore, EvalRun

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Get high-level aggregated metrics for the dashboard summary header."""
    res_agents = await db.execute(select(func.count(Agent.id)))
    total_agents = res_agents.scalar() or 0

    res_turns = await db.execute(select(func.count(AgentTurnEvent.id)))
    total_turns = res_turns.scalar() or 0

    res_flagged = await db.execute(select(func.count(AnomalyScore.id)).where(AnomalyScore.flagged == True))
    total_flagged = res_flagged.scalar() or 0

    res_eval = await db.execute(select(EvalRun).order_by(EvalRun.created_at.desc()).limit(1))
    latest_eval = res_eval.scalars().first()

    precision = latest_eval.precision if latest_eval else 1.0
    recall = latest_eval.recall if latest_eval else 1.0
    fpr = latest_eval.false_positive_rate if latest_eval else 0.0

    return {
        "total_agents": total_agents,
        "total_turns_scored": total_turns,
        "total_flagged_turns": total_flagged,
        "flag_rate": round(total_flagged / max(1, total_turns), 4),
        "latest_precision": precision,
        "latest_recall": recall,
        "latest_fpr": fpr
    }


@router.get("/timeline/{agent_id}")
async def get_anomaly_timeline(agent_id: str, limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Get timeline of scored turns for Recharts time-series chart."""
    result = await db.execute(
        select(AgentTurnEvent, AnomalyScore)
        .join(AnomalyScore, AgentTurnEvent.id == AnomalyScore.turn_event_id)
        .where(AgentTurnEvent.agent_id == agent_id)
        .order_by(AgentTurnEvent.timestamp.asc())
        .limit(limit)
    )
    rows = result.all()

    timeline_data = []
    for turn, score in rows:
        timeline_data.append({
            "id": turn.id,
            "turn_number": turn.turn_number,
            "session_id": turn.session_id,
            "input_summary": turn.input_summary,
            "isolation_score": score.isolation_score,
            "mahalanobis_distance": score.mahalanobis_distance,
            "combined_score": score.combined_score,
            "suspicion_accumulator": score.suspicion_accumulator,
            "flagged": score.flagged,
            "timestamp": turn.timestamp.isoformat()
        })
    return timeline_data


@router.get("/attribution/{agent_id}")
async def get_feature_attribution_summary(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get average feature attribution across flagged events for explanation breakdown."""
    result = await db.execute(
        select(AnomalyScore)
        .join(AgentTurnEvent, AnomalyScore.turn_event_id == AgentTurnEvent.id)
        .where(AgentTurnEvent.agent_id == agent_id, AnomalyScore.flagged == True)
        .limit(20)
    )
    scores = result.scalars().all()

    if not scores:
        return {"top_features": [], "message": "No flagged events yet"}

    feature_sums = {}
    count = float(len(scores))

    for sc in scores:
        attr = sc.feature_attribution or {}
        for fname, val in attr.items():
            feature_sums[fname] = feature_sums.get(fname, 0.0) + float(val)

    sorted_features = sorted(
        [{"feature": fname, "avg_importance": round(val / count, 4)} for fname, val in feature_sums.items()],
        key=lambda x: x["avg_importance"],
        reverse=True
    )
    return {"top_features": sorted_features}
