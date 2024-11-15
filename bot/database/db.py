from typing import Annotated
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


# Создаём ассоциации для типов
id_type = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
date = Annotated[datetime.datetime, mapped_column()]

# Объявляем базу данных
Base = declarative_base() 

# Создание асинхронного движка SQLAlchemy
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost/test"
engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Создание асинхронной сессии SQLAlchemy
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)