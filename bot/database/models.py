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