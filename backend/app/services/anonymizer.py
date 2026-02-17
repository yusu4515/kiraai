"""Anonymization service for learning data collection

Removes or replaces personally identifiable information (PII)
from hearing conversations and document data before storing
as training data.
"""

import re


# Patterns for Japanese PII
_PHONE_RE = re.compile(r'0\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4}')
_EMAIL_RE = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
_ZIPCODE_RE = re.compile(r'〒?\d{3}[-\s]?\d{4}')

# Common Japanese name patterns (simplified)
_KATAKANA_NAME_RE = re.compile(r'[ァ-ヶー]{2,6}\s?[ァ-ヶー]{2,6}')


def anonymize_text(text: str) -> str:
    """Replace PII in free text with placeholders"""
    if not text:
        return text

    result = text
    result = _PHONE_RE.sub('[電話番号]', result)
    result = _EMAIL_RE.sub('[メールアドレス]', result)
    result = _ZIPCODE_RE.sub('[郵便番号]', result)

    return result


def anonymize_conversation(conversation_log: list[dict]) -> list[dict]:
    """Anonymize a full conversation log

    Replaces names, phone numbers, emails, addresses in messages.
    Preserves the structure (role, content) for training.
    """
    if not conversation_log:
        return []

    anonymized = []
    detected_name = None

    for msg in conversation_log:
        content = msg.get("content", "")
        role = msg.get("role", "user")

        # Anonymize PII in content
        anon_content = anonymize_text(content)

        # If we detected a name from extracted data, replace it
        if detected_name and len(detected_name) >= 2:
            anon_content = anon_content.replace(detected_name, '[氏名]')

        anonymized.append({"role": role, "content": anon_content})

    return anonymized


def anonymize_extracted_data(extracted: dict) -> dict:
    """Anonymize extracted hearing data

    Keeps structure and general info but removes identifiable details.
    """
    if not extracted:
        return {}

    anon = {}

    for key, value in extracted.items():
        if key == "full_name":
            anon[key] = "[氏名]"
        elif key in ("phone", "email", "address"):
            anon[key] = f"[{key}]"
        elif key == "work_history" and isinstance(value, list):
            anon[key] = [
                {
                    "company": "[企業名]",
                    "period": item.get("period", ""),
                    "position": item.get("position", ""),
                    "duties": anonymize_text(item.get("duties", "")),
                    "achievements": anonymize_text(item.get("achievements", "")),
                }
                for item in value
            ]
        elif isinstance(value, str):
            anon[key] = anonymize_text(value)
        elif isinstance(value, dict):
            anon[key] = anonymize_extracted_data(value)
        elif isinstance(value, list):
            anon[key] = [
                anonymize_text(v) if isinstance(v, str) else v
                for v in value
            ]
        else:
            anon[key] = value

    return anon


def anonymize_profile_data(profile: dict) -> dict:
    """Anonymize profile data used for document generation

    Preserves career info structure but removes PII.
    """
    if not profile:
        return {}

    anon = {
        "full_name": "[氏名]",
        "birth_date": "[生年月日]",
        "phone": "[電話番号]",
        "address": "[住所]",
    }

    # Keep non-PII fields
    for key in ("education", "skills", "certifications", "languages",
                "preferences", "self_pr", "career_vision",
                "resignation_reason_positive"):
        if key in profile:
            val = profile[key]
            if isinstance(val, str):
                anon[key] = anonymize_text(val)
            elif isinstance(val, list):
                anon[key] = [
                    anonymize_text(v) if isinstance(v, str) else v
                    for v in val
                ]
            else:
                anon[key] = val

    # Anonymize work history
    if "work_history" in profile and isinstance(profile["work_history"], list):
        anon["work_history"] = [
            {
                "company": "[企業名]",
                "period": item.get("period", ""),
                "position": item.get("position", ""),
                "duties": anonymize_text(str(item.get("duties", ""))),
                "achievements": anonymize_text(str(item.get("achievements", ""))),
            }
            for item in profile["work_history"]
        ]

    return anon
