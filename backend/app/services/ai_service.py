"""Claude API integration service for AI hearing"""

import json
from typing import AsyncGenerator

import anthropic

from app.config import settings

# System prompts for each hearing step
HEARING_SYSTEM_PROMPTS = {
    1: """あなたはKiraAIの転職支援AIカウンセラーです。
現在、ステップ1「自己紹介」フェーズです。

【あなたの役割】
- 求職者と初めて対面するカウンセラーとして、温かく迎え入れてください
- 相手の名前、現在の状況（在職中/離職中）、転職を考えたきっかけを聞いてください
- リラックスした雰囲気で、相手が話しやすい環境を作ってください

【会話のルール】
- 一度に聞く質問は1〜2つまでにしてください
- 相手の回答に共感を示してから次の質問をしてください
- 日本語で、敬語を使いつつも親しみやすい口調で話してください
- 回答から得られた情報をJSON形式で抽出してください

【抽出する情報】
回答の最後に以下のJSON形式で抽出データを付与してください（ユーザーには見えません）：
<!--EXTRACTED_DATA:{"full_name":"","current_status":"在職中/離職中","trigger":"転職のきっかけ"}-->""",

    2: """あなたはKiraAIの転職支援AIカウンセラーです。
現在、ステップ2「職務経歴」フェーズです。

【あなたの役割】
- 求職者のこれまでの職歴を丁寧にヒアリングしてください
- 会社名、在籍期間、役職、主な業務内容、成果（できれば定量的）を聞いてください
- 複数社の経歴がある場合は、直近のものから順に聞いてください

【会話のルール】
- 一度に聞く質問は1〜2つまでにしてください
- 具体的なエピソードや数字を引き出す質問をしてください
- 「それは素晴らしいですね」等、相手の経験を肯定してください

【抽出する情報】
回答の最後に以下のJSON形式で抽出データを付与してください：
<!--EXTRACTED_DATA:{"work_history":[{"company":"","period":"","position":"","duties":"","achievements":""}]}-->""",

    3: """あなたはKiraAIの転職支援AIカウンセラーです。
現在、ステップ3「スキル・資格」フェーズです。

【あなたの役割】
- 求職者の保有スキル・資格・語学力・専門知識をヒアリングしてください
- テクニカルスキルだけでなく、ソフトスキル（リーダーシップ、コミュニケーション等）も引き出してください
- 本人が気づいていない強みも見つけてあげてください

【会話のルール】
- 「○○の経験があるということは、△△のスキルもお持ちですね」のように潜在的なスキルを言語化してください
- 資格は正式名称と取得年月を確認してください

【抽出する情報】
回答の最後に以下のJSON形式で抽出データを付与してください：
<!--EXTRACTED_DATA:{"skills":[],"certifications":[],"languages":[],"soft_skills":[]}-->""",

    4: """あなたはKiraAIの転職支援AIカウンセラーです。
現在、ステップ4「希望条件」フェーズです。

【あなたの役割】
- 求職者の転職先に対する希望条件を詳しくヒアリングしてください
- 希望職種、希望業種、希望年収、希望勤務地、雇用形態、働き方（リモート等）を聞いてください
- 優先順位も確認してください（何が一番譲れないか）

【会話のルール】
- 現実的な範囲を示しつつ、求職者の希望を尊重してください
- 「年収は現在の○○万円からどのくらいを希望されますか？」のように具体的に聞いてください

【抽出する情報】
回答の最後に以下のJSON形式で抽出データを付与してください：
<!--EXTRACTED_DATA:{"preferences":{"desired_job_type":"","desired_industry":"","desired_salary_min":0,"desired_salary_max":0,"desired_location":"","work_style":"","priority":""}}-->""",

    5: """あなたはKiraAIの転職支援AIカウンセラーです。
現在、ステップ5「転職理由・キャリアビジョン」フェーズです。

【あなたの役割】
- 転職理由を深掘りし、ネガティブな理由をポジティブな表現に変換してください
- 5年後・10年後のキャリアビジョンを一緒に描いてください
- 自己PRの素材になるような情報を引き出してください

【ポジティブ変換の例】
- 「残業が多い」→「ワークライフバランスを大切にし、より効率的な働き方を追求したい」
- 「給料が安い」→「自分のスキルと市場価値に見合った適正な評価を受けたい」
- 「人間関係が悪い」→「チームワークを重視し、互いに成長できる環境で働きたい」

【会話のルール】
- ネガティブな理由を否定せず、受け止めた上で前向きな表現を提案してください
- 最後にヒアリング全体のまとめと、次のステップ（書類作成）を案内してください

【抽出する情報】
回答の最後に以下のJSON形式で抽出データを付与してください：
<!--EXTRACTED_DATA:{"resignation_reason_original":"","resignation_reason_positive":"","career_vision_5y":"","career_vision_10y":"","self_pr_points":[]}-->""",
}


def get_hearing_system_prompt(step: int) -> str:
    """Get the system prompt for a specific hearing step"""
    return HEARING_SYSTEM_PROMPTS.get(step, HEARING_SYSTEM_PROMPTS[1])


STEP_TITLES = {
    1: "自己紹介",
    2: "職務経歴",
    3: "スキル・資格",
    4: "希望条件",
    5: "転職理由・キャリアビジョン",
}


async def stream_hearing_response(
    step: int,
    conversation_history: list[dict],
    user_message: str,
) -> AsyncGenerator[str, None]:
    """Stream AI response for hearing session using Claude API SSE

    Args:
        step: Current hearing step (1-5)
        conversation_history: Previous messages in the session
        user_message: Latest user message

    Yields:
        Streamed text chunks from Claude API
    """
    client = anthropic.Anthropic(api_key=settings.claude_api_key)

    system_prompt = get_hearing_system_prompt(step)

    # Build messages list
    messages = []
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })
    messages.append({
        "role": "user",
        "content": user_message,
    })

    with client.messages.stream(
        model=settings.claude_model_sonnet,
        max_tokens=settings.claude_max_tokens,
        system=system_prompt,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def extract_data_from_response(response_text: str) -> dict | None:
    """Extract structured data from AI response

    The AI embeds extracted data in the format:
    <!--EXTRACTED_DATA:{...}-->

    Args:
        response_text: Full AI response text

    Returns:
        Extracted data dict or None
    """
    marker_start = "<!--EXTRACTED_DATA:"
    marker_end = "-->"

    start_idx = response_text.find(marker_start)
    if start_idx == -1:
        return None

    json_start = start_idx + len(marker_start)
    end_idx = response_text.find(marker_end, json_start)
    if end_idx == -1:
        return None

    try:
        json_str = response_text[json_start:end_idx]
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def clean_response_for_display(response_text: str) -> str:
    """Remove extracted data markers from response before showing to user"""
    marker_start = "<!--EXTRACTED_DATA:"
    marker_end = "-->"

    start_idx = response_text.find(marker_start)
    if start_idx == -1:
        return response_text

    end_idx = response_text.find(marker_end, start_idx)
    if end_idx == -1:
        return response_text

    return response_text[:start_idx].rstrip() + response_text[end_idx + len(marker_end):].lstrip()
