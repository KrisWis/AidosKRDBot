from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base, date


# Таблица с данными пользователей
class UsersOrm(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String())
    user_reg_date: Mapped[date] = mapped_column(nullable=False)
    user_geo: Mapped[str] = mapped_column(String(), nullable=False)

    referer_id: Mapped[int | None] = mapped_column(BigInteger(), ForeignKey('users.user_id', ondelete='CASCADE'))
    referer: Mapped["UsersOrm"] = relationship("UsersOrm", foreign_keys=[referer_id], viewonly=True)

    __table_args__ = (
        UniqueConstraint('user_id', name='unique_user'),
    )


# Таблица c данными о прошедших концертах
class PreviousConcertsOrm(Base):
    __tablename__ = "previous_concerts"
    
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String())
    info_text: Mapped[str] = mapped_column(String())
    info_file_ids: Mapped[list[str]] = mapped_column(ARRAY(String()), nullable=True)

    __table_args__ = (
        UniqueConstraint('id', name='unique_concert'),
    )