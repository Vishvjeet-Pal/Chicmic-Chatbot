from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings 
from sqlalchemy import create_engine
engine_sync = create_engine(settings.DATABASE_URL.replace("+aiosqlite",""))
engine = create_async_engine(settings.DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()