"""Learning data collection service - anonymizes and stores AI interaction data"""

import re
from sqlalchemy.orm import Session

from app.models.learning_data import LearningData


def _anonymize_text(text: str) -> str:
    """Remove PII from text"""
    # Phone numbers
    text = re.sub(r'\d{2,4}-\d{2,4}-\d{4}', '[PHONE]', text)
    text = re.sub(r'0\d{9,10}', '[PHONE]', text)
    # Email
    text = re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+', '[EMAIL]', text)
    # Addresses (Japanese postal code + rough address pattern)
    text = re.sub(r'\d{3}-\d{4}', '[POSTAL]', text)
    return text


def _anonymize_dict(data: dict) -> dict:
    """Anonymize PII in a dict (shallow)"""
    result = {}
    pii_keys = {"email", "phone", "address", "full_name", "birth_date"}
    for key, value in data.items():
        if key in pii_keys:
            result[key] = "[REDACTED]"
        elif isinstance(value, str):
            result[key] = _anonymize_text(value)
        elif isinstance(value, list):
            result[key] = [_anonymize_text(str(v)) if isinstance(v, str) else v for v in value]
        else:
            result[key] = value
    return result


def record_hearing_data(
    db: Session,
    conversation_log: list[dict],
    extracted_data: dict,
    step: int,
):
    """Record anonymized hearing conversation for training"""
    anonymized_conv = []
    for msg in conversation_log:
        anonymized_conv.append({
            "role": msg.get("role"),
            "content": _anonymize_text(msg.get("content", "")),
        })

    entry = LearningData(
        data_type="hearing",
        input_data={"conversation": anonymized_conv},
        output_data=_anonymize_dict(extracted_data) if extracted_data else {},
        metadata_={"step": step},
    )
    db.add(entry)
    db.commit()


def record_document_data(
    db: Session,
    document_type: str,
    profile_data: dict,
    generated_html: str,
):
    """Record anonymized document generation for training"""
    entry = LearningData(
        data_type="document",
        input_data=_anonymize_dict(profile_data),
        output_data={"html_length": len(generated_html), "document_type": document_type},
        metadata_={"document_type": document_type},
    )
    db.add(entry)
    db.commit()


def get_learning_data_stats(db: Session) -> dict:
    """Get statistics about collected learning data"""
    total = db.query(LearningData).count()
    hearing_count = db.query(LearningData).filter(LearningData.data_type == "hearing").count()
    document_count = db.query(LearningData).filter(LearningData.data_type == "document").count()
    return {
        "total": total,
        "hearing": hearing_count,
        "document": document_count,
    }


def export_learning_data(db: Session, data_type: str | None = None) -> list[dict]:
    """Export learning data as list of dicts"""
    query = db.query(LearningData)
    if data_type:
        query = query.filter(LearningData.data_type == data_type)

    entries = query.order_by(LearningData.created_at.desc()).limit(1000).all()
    return [
        {
            "id": str(e.id),
            "data_type": e.data_type,
            "input_data": e.input_data,
            "output_data": e.output_data,
            "metadata": e.metadata_,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]
