"""Agent management API endpoints"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.agent import Agent
from app.utils.auth import get_current_user
from app.schemas.agent import AgentProfileUpdate, AgentProfileResponse, AgentDashboardResponse

router = APIRouter(prefix="/api/agent", tags=["agent"])


def _require_agent(current_user: User):
    if current_user.role != "agent":
        raise HTTPException(status_code=403, detail="Agent role required")
    return current_user


@router.get("/dashboard", response_model=AgentDashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get agent dashboard with profile and stats"""
    _require_agent(current_user)

    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        # Auto-create agent profile
        agent = Agent(
            user_id=current_user.id,
            company_name=current_user.full_name or "未設定",
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)

    # Basic stats (placeholder for now)
    stats = {
        "page_views": 0,
        "profile_views": 0,
        "inquiries": 0,
        "plan": agent.plan,
    }

    return AgentDashboardResponse(
        profile=AgentProfileResponse.model_validate(agent),
        stats=stats,
    )


@router.get("/profile", response_model=AgentProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get agent profile"""
    _require_agent(current_user)

    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent profile not found")

    return AgentProfileResponse.model_validate(agent)


@router.put("/profile", response_model=AgentProfileResponse)
def update_profile(
    request: AgentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update agent profile"""
    _require_agent(current_user)

    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        agent = Agent(
            user_id=current_user.id,
            company_name=request.company_name or current_user.full_name or "未設定",
        )
        db.add(agent)

    if request.company_name is not None:
        agent.company_name = request.company_name
    if request.description is not None:
        agent.description = request.description
    if request.logo_url is not None:
        agent.logo_url = request.logo_url
    if request.website_url is not None:
        agent.website_url = request.website_url
    agent.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(agent)
    return AgentProfileResponse.model_validate(agent)
