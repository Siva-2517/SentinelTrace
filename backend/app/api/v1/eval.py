from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.db_models import Agent, BaselineProfile, EvalRun
from app.models.schemas import EvalRunResponse
from app.simulation.eval_harness import eval_harness_instance

router = APIRouter(prefix="/eval", tags=["Evaluation"])


@router.post("/run/{agent_id}", response_model=EvalRunResponse, status_code=status.HTTP_201_CREATED)
async def run_evaluation_suite(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Run full evaluation harness (normal + injected scenarios) and calculate metrics."""
    result = await db.execute(
        select(BaselineProfile)
        .where(BaselineProfile.agent_id == agent_id)
        .order_by(BaselineProfile.version.desc())
    )
    baseline = result.scalars().first()
    if not baseline:
        raise HTTPException(status_code=400, detail="Agent has no fitted baseline. Build baseline first.")

    metrics = await eval_harness_instance.run_evaluation(
        baseline.feature_means,
        baseline.feature_covariance,
        baseline.isolation_forest_serialized
    )

    eval_run = EvalRun(
        agent_id=agent_id,
        run_type="injection_simulation",
        precision=metrics["precision"],
        recall=metrics["recall"],
        false_positive_rate=metrics["false_positive_rate"],
        threshold_used=metrics["threshold_used"],
        results=metrics
    )
    db.add(eval_run)
    await db.commit()
    await db.refresh(eval_run)
    return eval_run


@router.get("/runs/{agent_id}", response_model=List[EvalRunResponse])
async def list_eval_runs(agent_id: str, db: AsyncSession = Depends(get_db)):
    """List historical evaluation runs for an agent."""
    result = await db.execute(
        select(EvalRun)
        .where(EvalRun.agent_id == agent_id)
        .order_by(EvalRun.created_at.desc())
    )
    runs = result.scalars().all()
    return runs
