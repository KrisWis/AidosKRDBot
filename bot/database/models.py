from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base, date


# Таблица с общими данными пользователей
class UsersOrm(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String())
    user_reg_date: Mapped[date] = mapped_column(nullable=False)
    user_geo: Mapped[str] = mapped_column(String(), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', name='unique_user'),
    )