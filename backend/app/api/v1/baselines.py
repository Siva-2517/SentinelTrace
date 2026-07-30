from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.db_models import Agent, BaselineProfile
from app.models.schemas import BaselineProfileResponse
from app.services.baseline_service import build_baseline_profile

router = APIRouter(prefix="/agents/{agent_id}/baseline", tags=["Baselines"])


@router.post("/build", response_model=BaselineProfileResponse, status_code=status.HTTP_201_CREATED)
async def build_baseline(agent_id: str, scenario_count: int = 20, db: AsyncSession = Depends(get_db)):
    """Triggers synthetic normal scenario generation, extracts features, and fits Isolation Forest + Mahalanobis baseline."""
    try:
        baseline = await build_baseline_profile(agent_id, scenario_count, db)
        return baseline
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=BaselineProfileResponse)
async def get_latest_baseline(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get latest baseline profile for an agent."""
    result = await db.execute(
        select(BaselineProfile)
        .where(BaselineProfile.agent_id == agent_id)
        .order_by(BaselineProfile.version.desc())
    )
    baseline = result.scalars().first()
    if not baseline:
        raise HTTPException(status_code=404, detail="No baseline profile found for this agent")
    return baseline
