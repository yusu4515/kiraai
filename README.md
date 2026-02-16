# KiraAI - AI転職支援プラットフォーム

AIが「エージェント」「カウンセラー」「秘書」の一人三役で転職活動を完結させる統合プラットフォーム

## 概要

KiraAIは、複数の転職サイトを跨ぐ情報の断絶を解消し、求職者に完全無料でAI支援による転職活動をサポートします。

### 主な機能（Phase 1）

- 🤖 **AIヒアリング**: Claude APIによる対話型の深掘りヒアリング（5ステップ）
- 📄 **書類自動生成**: 履歴書・職務経歴書をPDF/Word形式で自動生成
- 🔍 **求人検索**: Indeed APIなど複数媒体を横断した求人検索
- 📋 **応募管理カンバン**: ドラッグ&ドロップで応募ステータスを管理
- 🏢 **エージェント管理画面**: 転職エージェント向けの掲載情報管理・レポート機能
- 📊 **学習データ収集**: AI品質向上のためのデータパイプライン

## 技術スタック

### Frontend
- React 18 + TypeScript
- Vite（ビルドツール）
- TailwindCSS（スタイリング）
- Zustand（状態管理）
- React Router（ルーティング）

### Backend
- FastAPI (Python 3.12)
- PostgreSQL 16（メインDB）
- Redis 7.2（キャッシュ・セッション）
- SQLAlchemy 2.0（ORM）
- Anthropic Claude API（AI）

### Infrastructure
- Docker & Docker Compose
- Nginx（リバースプロキシ）

## セットアップ手順

### 前提条件

- Docker Desktop 24+
- Python 3.12+
- Node.js 20+
- Git

### 初回起動

```bash
# 1. リポジトリをクローン（または既存ディレクトリに移動）
cd "C:\Users\yusuk\OneDrive\デスクトップ\開発\KIRA.AI"

# 2. 環境変数を設定
cp .env.example .env
# .envファイルを編集して、CLAUDE_API_KEY等を設定

# 3. Dockerコンテナを起動
docker-compose up -d

# 4. データベースマイグレーション
docker-compose exec backend alembic upgrade head

# 5. アプリケーションにアクセス
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
```

### 開発時のコマンド

```bash
# ログ確認
docker-compose logs -f backend
docker-compose logs -f frontend

# コンテナ再ビルド
docker-compose up -d --build

# データベースリセット
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head

# バックエンドのみ再起動
docker-compose restart backend

# フロントエンドのみ再起動
docker-compose restart frontend
```

## プロジェクト構造

```
KIRA.AI/
├── docker-compose.yml      # 全サービスのオーケストレーション
├── .env.example            # 環境変数テンプレート
├── .gitignore              # Git除外設定
├── README.md               # このファイル
├── docs/                   # ドキュメント
├── frontend/               # React フロントエンド
│   ├── src/
│   └── package.json
├── backend/                # FastAPI バックエンド
│   ├── app/
│   ├── pyproject.toml
│   └── Dockerfile
├── infra/                  # インフラ設定
│   ├── postgres/
│   └── redis/
└── rpa/                    # RPA（Phase 2以降）
```

## API仕様

バックエンド起動後、以下のURLでAPI仕様を確認できます：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ビジネスモデル

- **求職者**: 完全無料
- **収益源**: 転職エージェントからの掲載料（メディア掲載費）
- **法的位置づけ**: 求人情報集約メディアサービス（職業紹介事業ではない）

## 開発ロードマップ

### Phase 1（現在）: MVP - 基本機能実装
- ✅ 基盤構築
- ⏳ 認証機能
- ⏳ AIヒアリング
- ⏳ 書類生成
- ⏳ 求人検索
- ⏳ 応募管理カンバン
- ⏳ エージェント管理画面
- ⏳ 学習データ収集

### Phase 2: RPA・収益化
- 複数転職サイトRPA連携
- エージェント掲載審査フロー
- ファインチューニング開始

### Phase 3: 専用AI・高度化
- 専用AIモデル本番稼働
- 企業深掘り分析
- AI面接トレーニング

### Phase 4: 完全版
- 専用AI完全自社運用
- スマートフォンアプリ対応

## ライセンス

© 2026 KiraAI. All rights reserved.

## お問い合わせ

開発に関する質問や提案は、GitHubのIssuesまでお願いします。
