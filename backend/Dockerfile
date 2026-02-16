FROM python:3.12-slim

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージのインストール（PDF生成に必要）
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Poetryをインストール
RUN pip install --no-cache-dir poetry==1.7.1

# Poetry設定（仮想環境を作成しない）
RUN poetry config virtualenvs.create false

# 依存関係ファイルをコピー
COPY pyproject.toml poetry.lock* ./

# 依存関係をインストール
RUN poetry install --no-root --no-interaction --no-ansi

# アプリケーションコードをコピー
COPY . .

# ヘルスチェック用のエンドポイント確認
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 起動コマンド（docker-compose.ymlでオーバーライド可能）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
