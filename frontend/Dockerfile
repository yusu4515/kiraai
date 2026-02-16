FROM node:20-alpine

# 作業ディレクトリ設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install

# アプリケーションコードをコピー
COPY . .

# 開発サーバーを起動（ポート3000）
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
