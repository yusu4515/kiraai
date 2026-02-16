"""AI Hearing API endpoints with SSE streaming"""

import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.hearing import HearingSession
from app.models.profile import Profile
from app.schemas.hearing import HearingSessionResponse, HearingStartResponse
from app.services.ai_service import (
    stream_hearing_response,
    extract_data_from_response,
    clean_response_for_display,
    STEP_TITLES,
)
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/start", response_model=HearingStartResponse)
def start_hearing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new hearing session

    Creates a new 5-step hearing session for the authenticated user.
    """
    session = HearingSession(
        user_id=current_user.id,
        current_step=1,
        conversation_log=[],
        extracted_data={},
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return HearingStartResponse(
        session_id=session.id,
        current_step=1,
        step_title=STEP_TITLES[1],
        greeting="こんにちは！KiraAIの転職支援カウンセラーです。あなたの転職活動をサポートさせてください。まずは自己紹介からお伺いしますね。お名前と、現在のご状況（在職中・離職中など）を教えていただけますか？",
    )


@router.get("/session/{session_id}", response_model=HearingSessionResponse)
def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get hearing session details"""
    session = db.query(HearingSession).filter(
        HearingSession.id == session_id,
        HearingSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.post("/stream")
async def stream_hearing(
    session_id: str = Query(...),
    message: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stream AI hearing response via SSE

    Args:
        session_id: UUID of the hearing session
        message: User's message text

    Returns:
        SSE stream of AI response chunks
    """
    # Get session
    session = db.query(HearingSession).filter(
        HearingSession.id == session_id,
        HearingSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.is_completed:
        raise HTTPException(status_code=400, detail="Session already completed")

    # Add user message to conversation log
    conversation_log = session.conversation_log or []
    conversation_log.append({"role": "user", "content": message})

    async def event_generator():
        full_response = ""

        try:
            async for chunk in stream_hearing_response(
                step=session.current_step,
                conversation_history=conversation_log[:-1],  # exclude current message
                user_message=message,
            ):
                full_response += chunk
                # Send SSE event
                data = json.dumps({"type": "chunk", "content": chunk}, ensure_ascii=False)
                yield f"data: {data}\n\n"

            # Extract data from full response
            extracted = extract_data_from_response(full_response)
            clean_response = clean_response_for_display(full_response)

            # Update session in DB
            conversation_log.append({"role": "assistant", "content": clean_response})
            session.conversation_log = conversation_log

            if extracted:
                current_extracted = session.extracted_data or {}
                current_extracted.update(extracted)
                session.extracted_data = current_extracted

            db.add(session)
            db.commit()

            # Send completion event with step info
            step_data = {
                "type": "done",
                "current_step": session.current_step,
                "step_title": STEP_TITLES.get(session.current_step, ""),
                "extracted_data": extracted,
            }
            yield f"data: {json.dumps(step_data, ensure_ascii=False)}\n\n"

        except Exception as e:
            error_data = json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/session/{session_id}/next-step", response_model=HearingSessionResponse)
def advance_step(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Advance to the next hearing step

    Moves the session to the next step (1->2->3->4->5->complete).
    """
    session = db.query(HearingSession).filter(
        HearingSession.id == session_id,
        HearingSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.is_completed:
        raise HTTPException(status_code=400, detail="Session already completed")

    if session.current_step >= 5:
        # Complete the session and save profile
        session.is_completed = True
        _save_profile_from_hearing(session, current_user, db)
    else:
        session.current_step += 1

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def _save_profile_from_hearing(session: HearingSession, user: User, db: Session):
    """Save extracted hearing data to user profile"""
    extracted = session.extracted_data or {}

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)

    # Map extracted data to profile fields
    if "full_name" in extracted:
        profile.full_name = extracted["full_name"]
    if "work_history" in extracted:
        profile.work_history = extracted["work_history"]
    if "skills" in extracted:
        profile.skills = extracted["skills"]
    if "certifications" in extracted:
        profile.certifications = extracted["certifications"]
    if "languages" in extracted:
        profile.languages = extracted["languages"]
    if "preferences" in extracted:
        profile.preferences = extracted["preferences"]
    if "resignation_reason_original" in extracted:
        profile.resignation_reason_original = extracted["resignation_reason_original"]
    if "resignation_reason_positive" in extracted:
        profile.resignation_reason_positive = extracted["resignation_reason_positive"]
    if "career_vision_5y" in extracted or "career_vision_10y" in extracted:
        vision_parts = []
        if "career_vision_5y" in extracted:
            vision_parts.append(f"5年後: {extracted['career_vision_5y']}")
        if "career_vision_10y" in extracted:
            vision_parts.append(f"10年後: {extracted['career_vision_10y']}")
        profile.career_vision = "\n".join(vision_parts)
    if "self_pr_points" in extracted:
        profile.self_pr = "、".join(extracted["self_pr_points"])

    db.add(profile)
