from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session class for database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
