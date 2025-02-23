from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 创建会话类，用来连接数据库
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
