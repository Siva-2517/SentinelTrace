from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.db_models import Agent
from app.models.schemas import AgentCreate, AgentResponse
from app.agent.tools import TOOL_MANIFEST

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def register_agent(agent_in: AgentCreate, db: Session = Depends(get_db)):
    """Register a new LangGraph agent for behavioral monitoring."""
    manifest = agent_in.tool_manifest if agent_in.tool_manifest else TOOL_MANIFEST

    agent = Agent(
        name=agent_in.name,
        system_prompt=agent_in.system_prompt,
        tool_manifest=manifest,
        status="active"
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("", response_model=List[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    """List all registered agents."""
    agents = db.query(Agent).all()
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get details of a specific agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
