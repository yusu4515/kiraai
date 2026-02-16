-- KiraAI Database Initialization Script
-- このスクリプトはPostgreSQLコンテナ初回起動時に自動実行されます

-- UUID拡張を有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- タイムゾーン設定
SET timezone = 'Asia/Tokyo';

-- 初期データベース作成確認
\echo 'KiraAI Database Initialization Started'

-- 注意: テーブル作成はAlembicマイグレーションで行うため、
-- ここでは拡張機能の有効化のみを行います

\echo 'KiraAI Database Initialization Completed'
