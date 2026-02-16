"""Document generation service - Resume and Career Sheet"""

import anthropic

from app.config import settings


RESUME_SYSTEM_PROMPT = """あなたは日本の転職市場に精通した履歴書作成の専門家です。
提供されたプロフィール情報を基に、日本標準フォーマットの履歴書をHTML形式で生成してください。

【生成ルール】
- 日本の標準的な履歴書（JIS規格準拠）のレイアウトを再現してください
- すべての項目を丁寧に記載してください
- 情報が不足している場合は「（未入力）」と記載してください
- HTMLのみを出力してください（説明文は不要）
- CSSはインラインスタイルで記載してください
- A4サイズ（210mm x 297mm）に収まるレイアウトにしてください
- フォントはNoto Sans JPを使用してください
- 印刷時にきれいに出力されるようにしてください"""

CAREER_SHEET_SYSTEM_PROMPT = """あなたは日本の転職市場に精通した職務経歴書作成の専門家です。
提供されたプロフィール情報を基に、職務経歴書をHTML形式で生成してください。

【生成ルール】
- 「職務要約」「職務経歴詳細」「活かせるスキル・知識」「自己PR」のセクションを含めてください
- 職務経歴は逆時系列（直近が上）で記載してください
- 成果は可能な限り定量的に記載してください
- HTMLのみを出力してください（説明文は不要）
- CSSはインラインスタイルで記載してください
- A4サイズに収まるレイアウトにしてください
- フォントはNoto Sans JPを使用してください
- ビジネス文書として適切なフォーマットにしてください"""


def _build_profile_text(profile_data: dict) -> str:
    """Build a text representation of profile data for AI input"""
    parts = []

    if profile_data.get("full_name"):
        parts.append(f"氏名: {profile_data['full_name']}")
    if profile_data.get("birth_date"):
        parts.append(f"生年月日: {profile_data['birth_date']}")
    if profile_data.get("phone"):
        parts.append(f"電話番号: {profile_data['phone']}")
    if profile_data.get("address"):
        parts.append(f"住所: {profile_data['address']}")

    education = profile_data.get("education", [])
    if education:
        parts.append("\n【学歴】")
        for edu in education:
            if isinstance(edu, dict):
                parts.append(f"  - {edu.get('school', '')} {edu.get('faculty', '')} ({edu.get('year', '')})")
            else:
                parts.append(f"  - {edu}")

    work_history = profile_data.get("work_history", [])
    if work_history:
        parts.append("\n【職歴】")
        for work in work_history:
            if isinstance(work, dict):
                parts.append(f"  会社名: {work.get('company', '')}")
                parts.append(f"  期間: {work.get('period', '')}")
                parts.append(f"  役職: {work.get('position', '')}")
                parts.append(f"  業務内容: {work.get('duties', '')}")
                parts.append(f"  実績: {work.get('achievements', '')}")
                parts.append("")
            else:
                parts.append(f"  - {work}")

    skills = profile_data.get("skills", [])
    if skills:
        parts.append(f"\n【スキル】\n  {', '.join(str(s) for s in skills)}")

    certifications = profile_data.get("certifications", [])
    if certifications:
        parts.append(f"\n【資格】\n  {', '.join(str(c) for c in certifications)}")

    languages = profile_data.get("languages", [])
    if languages:
        parts.append(f"\n【語学】\n  {', '.join(str(l) for l in languages)}")

    if profile_data.get("self_pr"):
        parts.append(f"\n【自己PR】\n  {profile_data['self_pr']}")

    if profile_data.get("career_vision"):
        parts.append(f"\n【キャリアビジョン】\n  {profile_data['career_vision']}")

    if profile_data.get("resignation_reason_positive"):
        parts.append(f"\n【転職理由（ポジティブ版）】\n  {profile_data['resignation_reason_positive']}")

    preferences = profile_data.get("preferences", {})
    if preferences:
        parts.append("\n【希望条件】")
        if isinstance(preferences, dict):
            for key, value in preferences.items():
                parts.append(f"  {key}: {value}")

    return "\n".join(parts) if parts else "プロフィール情報が登録されていません。"


def _fallback_resume_html(profile_data: dict) -> str:
    """Generate resume HTML using a template (fallback when no API key)"""
    name = profile_data.get("full_name", "（未入力）")
    birth_date = profile_data.get("birth_date", "（未入力）")
    phone = profile_data.get("phone", "（未入力）")
    address = profile_data.get("address", "（未入力）")

    education_rows = ""
    for edu in profile_data.get("education", []):
        if isinstance(edu, dict):
            education_rows += f"<tr><td>{edu.get('year', '')}</td><td>{edu.get('school', '')} {edu.get('faculty', '')}</td></tr>"
        else:
            education_rows += f"<tr><td></td><td>{edu}</td></tr>"
    if not education_rows:
        education_rows = "<tr><td colspan='2'>（未入力）</td></tr>"

    work_rows = ""
    for work in profile_data.get("work_history", []):
        if isinstance(work, dict):
            work_rows += f"<tr><td>{work.get('period', '')}</td><td>{work.get('company', '')} - {work.get('position', '')}<br>{work.get('duties', '')}</td></tr>"
        else:
            work_rows += f"<tr><td></td><td>{work}</td></tr>"
    if not work_rows:
        work_rows = "<tr><td colspan='2'>（未入力）</td></tr>"

    skills = ", ".join(str(s) for s in profile_data.get("skills", [])) or "（未入力）"
    certifications = ", ".join(str(c) for c in profile_data.get("certifications", [])) or "（未入力）"
    self_pr = profile_data.get("self_pr", "（未入力）")

    return f"""<div style="font-family: 'Noto Sans JP', sans-serif; max-width: 210mm; margin: 0 auto; padding: 20mm; font-size: 10pt; line-height: 1.6;">
  <h1 style="text-align: center; font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 8px; margin-bottom: 20px;">履 歴 書</h1>
  <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
    <tr><th style="text-align: left; width: 100px; padding: 6px; border: 1px solid #ccc; background: #f5f5f5;">氏名</th><td style="padding: 6px; border: 1px solid #ccc; font-size: 14pt; font-weight: bold;">{name}</td></tr>
    <tr><th style="text-align: left; padding: 6px; border: 1px solid #ccc; background: #f5f5f5;">生年月日</th><td style="padding: 6px; border: 1px solid #ccc;">{birth_date}</td></tr>
    <tr><th style="text-align: left; padding: 6px; border: 1px solid #ccc; background: #f5f5f5;">電話番号</th><td style="padding: 6px; border: 1px solid #ccc;">{phone}</td></tr>
    <tr><th style="text-align: left; padding: 6px; border: 1px solid #ccc; background: #f5f5f5;">住所</th><td style="padding: 6px; border: 1px solid #ccc;">{address}</td></tr>
  </table>
  <h2 style="font-size: 12pt; border-bottom: 1px solid #666; padding-bottom: 4px; margin-top: 20px;">学歴</h2>
  <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
    <tr><th style="width: 120px; padding: 6px; border: 1px solid #ccc; background: #f5f5f5;">年月</th><th style="padding: 6px; border: 1px solid #ccc; background: #f5f5f5;">学校名・学部</th></tr>
    {education_rows}
  </table>
  <h2 style="font-size: 12pt; border-bottom: 1px solid #666; padding-bottom: 4px; margin-top: 20px;">職歴</h2>
  <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
    <tr><th style="width: 120px; padding: 6px; border: 1px solid #ccc; background: #f5f5f5;">期間</th><th style="padding: 6px; border: 1px solid #ccc; background: #f5f5f5;">会社名・職務内容</th></tr>
    {work_rows}
  </table>
  <h2 style="font-size: 12pt; border-bottom: 1px solid #666; padding-bottom: 4px; margin-top: 20px;">資格・スキル</h2>
  <p style="padding: 6px;"><strong>スキル:</strong> {skills}</p>
  <p style="padding: 6px;"><strong>資格:</strong> {certifications}</p>
  <h2 style="font-size: 12pt; border-bottom: 1px solid #666; padding-bottom: 4px; margin-top: 20px;">自己PR</h2>
  <p style="padding: 6px;">{self_pr}</p>
</div>"""


def _fallback_career_sheet_html(profile_data: dict) -> str:
    """Generate career sheet HTML using a template (fallback when no API key)"""
    name = profile_data.get("full_name", "（未入力）")

    work_sections = ""
    for work in profile_data.get("work_history", []):
        if isinstance(work, dict):
            work_sections += f"""<div style="margin-bottom: 16px; padding: 12px; border: 1px solid #ddd; border-radius: 4px;">
  <h3 style="margin: 0 0 8px 0; font-size: 11pt;">{work.get('company', '（会社名未入力）')}</h3>
  <p style="margin: 4px 0; color: #666;">期間: {work.get('period', '（未入力）')} ｜ 役職: {work.get('position', '（未入力）')}</p>
  <p style="margin: 4px 0;"><strong>業務内容:</strong> {work.get('duties', '（未入力）')}</p>
  <p style="margin: 4px 0;"><strong>実績:</strong> {work.get('achievements', '（未入力）')}</p>
</div>"""
    if not work_sections:
        work_sections = "<p>（職歴情報が未入力です）</p>"

    skills = ", ".join(str(s) for s in profile_data.get("skills", [])) or "（未入力）"
    self_pr = profile_data.get("self_pr", "（未入力）")
    career_vision = profile_data.get("career_vision", "（未入力）")

    return f"""<div style="font-family: 'Noto Sans JP', sans-serif; max-width: 210mm; margin: 0 auto; padding: 20mm; font-size: 10pt; line-height: 1.6;">
  <h1 style="text-align: center; font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 8px; margin-bottom: 20px;">職 務 経 歴 書</h1>
  <p style="text-align: right; margin-bottom: 16px;">氏名: {name}</p>
  <h2 style="font-size: 12pt; border-bottom: 1px solid #666; padding-bottom: 4px; margin-top: 20px;">職務要約</h2>
  <p style="padding: 6px;">{career_vision}</p>
  <h2 style="font-size: 12pt; border-bottom: 1px solid #666; padding-bottom: 4px; margin-top: 20px;">職務経歴詳細</h2>
  {work_sections}
  <h2 style="font-size: 12pt; border-bottom: 1px solid #666; padding-bottom: 4px; margin-top: 20px;">活かせるスキル・知識</h2>
  <p style="padding: 6px;">{skills}</p>
  <h2 style="font-size: 12pt; border-bottom: 1px solid #666; padding-bottom: 4px; margin-top: 20px;">自己PR</h2>
  <p style="padding: 6px;">{self_pr}</p>
</div>"""


def generate_resume_html(profile_data: dict) -> str:
    """Generate resume HTML using Claude API (falls back to template if no API key)"""
    if not settings.claude_api_key:
        return _fallback_resume_html(profile_data)

    client = anthropic.Anthropic(api_key=settings.claude_api_key)

    profile_text = _build_profile_text(profile_data)

    response = client.messages.create(
        model=settings.claude_model_sonnet,
        max_tokens=settings.claude_max_tokens,
        system=RESUME_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"以下のプロフィール情報を基に、日本標準フォーマットの履歴書をHTML形式で生成してください。\n\n{profile_text}",
        }],
    )

    html = response.content[0].text

    # Strip markdown code block if present
    if html.startswith("```html"):
        html = html[7:]
    if html.startswith("```"):
        html = html[3:]
    if html.endswith("```"):
        html = html[:-3]

    return html.strip()


def generate_career_sheet_html(profile_data: dict) -> str:
    """Generate career sheet HTML using Claude API (falls back to template if no API key)"""
    if not settings.claude_api_key:
        return _fallback_career_sheet_html(profile_data)

    client = anthropic.Anthropic(api_key=settings.claude_api_key)

    profile_text = _build_profile_text(profile_data)

    response = client.messages.create(
        model=settings.claude_model_sonnet,
        max_tokens=settings.claude_max_tokens,
        system=CAREER_SHEET_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"以下のプロフィール情報を基に、職務経歴書をHTML形式で生成してください。\n\n{profile_text}",
        }],
    )

    html = response.content[0].text

    if html.startswith("```html"):
        html = html[7:]
    if html.startswith("```"):
        html = html[3:]
    if html.endswith("```"):
        html = html[:-3]

    return html.strip()
