import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 取得目前專案資料夾位置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite 資料庫位置
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'food.db')}"

# 建立資料庫引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 建立資料庫操作 Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 讓 models.py 中的資料表模型繼承使用
Base = declarative_base()


def get_db():
    """提供每次 API 請求使用的資料庫連線。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()