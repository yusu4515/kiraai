"""Job search service - search from DB cache and external APIs"""

import json
import hashlib
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.job import Job
from app.database import get_redis


def _cache_key(keyword: str, location: str | None, page: int) -> str:
    raw = f"{keyword}:{location or ''}:{page}"
    return f"jobs:search:{hashlib.md5(raw.encode()).hexdigest()}"


def search_jobs(
    db: Session,
    keyword: str,
    location: str | None = None,
    salary_min: int | None = None,
    job_type: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Job], int]:
    """Search jobs from local DB cache"""
    query = db.query(Job)

    # Keyword search in title, company_name, description
    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Job.title.ilike(like_pattern),
                Job.company_name.ilike(like_pattern),
                Job.description.ilike(like_pattern),
            )
        )

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if salary_min:
        query = query.filter(
            or_(Job.salary_min >= salary_min, Job.salary_max >= salary_min)
        )

    if job_type:
        query = query.filter(Job.job_type == job_type)

    total = query.count()
    jobs = (
        query.order_by(Job.posted_at.desc().nullslast())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return jobs, total


def seed_sample_jobs(db: Session) -> int:
    """Seed sample job data for development/testing"""
    existing = db.query(Job).count()
    if existing > 0:
        return 0

    sample_jobs = [
        Job(
            source="manual",
            title="Webエンジニア（フルスタック）",
            company_name="株式会社テックイノベーション",
            location="東京都渋谷区",
            salary_min=5000000,
            salary_max=8000000,
            description="React/TypeScript + Python/FastAPIを使用したWebアプリケーション開発。自社プロダクトの企画から開発まで一貫して担当。リモートワーク可。",
            requirements="実務経験3年以上、React経験必須、Python経験あれば尚可",
            job_type="full_time",
            url="https://example.com/job/1",
            posted_at=datetime(2026, 2, 10),
        ),
        Job(
            source="manual",
            title="バックエンドエンジニア（Python）",
            company_name="AIソリューションズ株式会社",
            location="東京都港区",
            salary_min=6000000,
            salary_max=10000000,
            description="AI/MLプラットフォームのバックエンド開発。FastAPI、PostgreSQL、Redisを使用。大規模データ処理の設計・実装。",
            requirements="Python実務3年以上、SQL経験必須、AI/ML知識あれば尚可",
            job_type="full_time",
            url="https://example.com/job/2",
            posted_at=datetime(2026, 2, 12),
        ),
        Job(
            source="manual",
            title="フロントエンドエンジニア",
            company_name="株式会社デジタルクリエイト",
            location="大阪府大阪市",
            salary_min=4500000,
            salary_max=7000000,
            description="ECサイトのフロントエンド刷新プロジェクト。Next.js/React/TypeScriptを使用。UI/UXデザイナーと協業。",
            requirements="React実務2年以上、TypeScript経験必須",
            job_type="full_time",
            url="https://example.com/job/3",
            posted_at=datetime(2026, 2, 8),
        ),
        Job(
            source="manual",
            title="インフラエンジニア（AWS）",
            company_name="クラウドネクスト株式会社",
            location="東京都千代田区",
            salary_min=5500000,
            salary_max=9000000,
            description="AWSを中心としたクラウドインフラの設計・構築・運用。Terraform/Kubernetes経験者歓迎。",
            requirements="AWS実務2年以上、Linux経験必須",
            job_type="full_time",
            url="https://example.com/job/4",
            posted_at=datetime(2026, 2, 14),
        ),
        Job(
            source="manual",
            title="データサイエンティスト",
            company_name="株式会社データインサイト",
            location="東京都新宿区",
            salary_min=6000000,
            salary_max=12000000,
            description="マーケティングデータの分析・予測モデル構築。Python/R、SQL、機械学習フレームワークを使用。",
            requirements="統計学・機械学習の知識、Python実務2年以上",
            job_type="full_time",
            url="https://example.com/job/5",
            posted_at=datetime(2026, 2, 11),
        ),
        Job(
            source="manual",
            title="モバイルアプリエンジニア（React Native）",
            company_name="アプリファクトリー株式会社",
            location="福岡県福岡市",
            salary_min=4000000,
            salary_max=6500000,
            description="ヘルスケアアプリの開発。React Native/TypeScriptを使用。iOS/Android同時開発。フルリモート可。",
            requirements="React Native実務1年以上、モバイルアプリ開発経験",
            job_type="full_time",
            url="https://example.com/job/6",
            posted_at=datetime(2026, 2, 9),
        ),
        Job(
            source="manual",
            title="プロジェクトマネージャー（IT）",
            company_name="株式会社システムパートナーズ",
            location="名古屋市中区",
            salary_min=5500000,
            salary_max=8500000,
            description="受託開発プロジェクトのPM業務。要件定義〜納品まで。アジャイル開発経験者歓迎。",
            requirements="PM経験3年以上、IT業界経験必須",
            job_type="full_time",
            url="https://example.com/job/7",
            posted_at=datetime(2026, 2, 13),
        ),
        Job(
            source="manual",
            title="QAエンジニア",
            company_name="品質テック株式会社",
            location="東京都品川区",
            salary_min=4000000,
            salary_max=6000000,
            description="Webアプリケーションの品質保証。テスト自動化（Playwright/Cypress）、CI/CD構築。",
            requirements="QA実務2年以上、テスト自動化経験あれば尚可",
            job_type="full_time",
            url="https://example.com/job/8",
            posted_at=datetime(2026, 2, 7),
        ),
        Job(
            source="manual",
            title="SREエンジニア",
            company_name="スケールアップ株式会社",
            location="東京都渋谷区",
            salary_min=7000000,
            salary_max=12000000,
            description="大規模SaaSプラットフォームの信頼性向上。Kubernetes/Prometheus/Grafana。オンコール対応あり。",
            requirements="SRE/インフラ経験3年以上、Kubernetes経験必須",
            job_type="full_time",
            url="https://example.com/job/9",
            posted_at=datetime(2026, 2, 15),
        ),
        Job(
            source="manual",
            title="機械学習エンジニア",
            company_name="AIラボ株式会社",
            location="東京都文京区",
            salary_min=7000000,
            salary_max=15000000,
            description="自然言語処理・LLMの研究開発。PyTorch/Transformers。論文執筆・学会発表の機会あり。",
            requirements="ML実務2年以上、NLP知識必須、博士号歓迎",
            job_type="full_time",
            url="https://example.com/job/10",
            posted_at=datetime(2026, 2, 16),
        ),
    ]

    db.add_all(sample_jobs)
    db.commit()
    return len(sample_jobs)
