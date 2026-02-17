"""Learning data collection service

Automatically records anonymized hearing conversations and
document generation data for future AI model improvement.
"""

import logging

from sqlalchemy.orm import Session

from app.models.learning_data import LearningData
from app.services.anonymizer import (
    anonymize_conversation,
    anonymize_extracted_data,
    anonymize_profile_data,
)

logger = logging.getLogger(__name__)


def record_hearing_data(
    db: Session,
    conversation_log: list[dict],
    extracted_data: dict,
    step: int,
    model_name: str = "",
) -> LearningData | None:
    """Record anonymized hearing session data

    Called when a hearing session completes (all 5 steps done).
    """
    try:
        anon_conversation = anonymize_conversation(conversation_log)
        anon_extracted = anonymize_extracted_data(extracted_data)

        entry = LearningData(
            data_type="hearing",
            input_data={
                "conversation": anon_conversation,
                "total_steps": step,
            },
            output_data={
                "extracted_profile": anon_extracted,
            },
            metadata_={
                "model": model_name,
                "message_count": len(conversation_log),
                "steps_completed": step,
            },
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        logger.info(f"Recorded hearing learning data: {entry.id}")
        return entry

    except Exception as e:
        logger.error(f"Failed to record hearing data: {e}", exc_info=True)
        db.rollback()
        return None


def record_document_data(
    db: Session,
    document_type: str,
    profile_data: dict,
    generated_html: str,
) -> LearningData | None:
    """Record anonymized document generation data

    Called when a document (resume/career_sheet) is generated.
    """
    try:
        anon_profile = anonymize_profile_data(profile_data)

        # Only keep first 2000 chars of HTML to save space
        truncated_html = generated_html[:2000] if generated_html else ""

        entry = LearningData(
            data_type="document",
            input_data={
                "document_type": document_type,
                "profile": anon_profile,
            },
            output_data={
                "html_preview": truncated_html,
                "html_length": len(generated_html) if generated_html else 0,
            },
            metadata_={
                "document_type": document_type,
            },
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        logger.info(f"Recorded document learning data: {entry.id}")
        return entry

    except Exception as e:
        logger.error(f"Failed to record document data: {e}", exc_info=True)
        db.rollback()
        return None
