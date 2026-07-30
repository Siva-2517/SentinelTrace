from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.db_models import Agent, BaselineProfile
from app.models.schemas import BaselineProfileResponse
from app.services.baseline_service import build_baseline_profile

router = APIRouter(prefix="/agents/{agent_id}/baseline", tags=["Baselines"])


@router.post("/build", response_model=BaselineProfileResponse, status_code=status.HTTP_201_CREATED)
async def build_baseline(agent_id: str, scenario_count: int = 20, db: Session = Depends(get_db)):
    """Triggers synthetic normal scenario generation, extracts features, and fits Isolation Forest + Mahalanobis baseline."""
    try:
        baseline = await build_baseline_profile(agent_id, scenario_count, db)
        return baseline
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=BaselineProfileResponse)
def get_latest_baseline(agent_id: str, db: Session = Depends(get_db)):
    """Get latest baseline profile for an agent."""
    baseline = db.query(BaselineProfile).filter(BaselineProfile.agent_id == agent_id).order_by(BaselineProfile.version.desc()).first()
    if not baseline:
        raise HTTPException(status_code=404, detail="No baseline profile found for this agent")
    return baseline
