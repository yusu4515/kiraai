"""Database connection and session management"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from redis import Redis

from app.config import settings

# PostgreSQL Engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 接続確認
    pool_size=10,  # 接続プールサイズ
    max_overflow=20,  # 最大オーバーフロー接続数
    echo=settings.debug,  # SQLログ出力（開発時のみ）
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """Database session dependency for FastAPI endpoints

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis connection
redis_client: Redis = Redis.from_url(
    settings.redis_url,
    decode_responses=True,  # 文字列として取得
    socket_connect_timeout=5,
    socket_timeout=5,
)


def get_redis() -> Redis:
    """Redis client dependency for FastAPI endpoints

    Usage:
        @app.get("/cache")
        def get_cache(redis: Redis = Depends(get_redis)):
            ...
    """
    return redis_client


def init_db() -> None:
    """Initialize database (create all tables)

    Note: 本番環境ではAlembicマイグレーションを使用するため、
    この関数は開発・テスト環境でのみ使用します。
    """
    Base.metadata.create_all(bind=engine)
