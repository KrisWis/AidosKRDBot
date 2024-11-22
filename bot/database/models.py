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
    created_at: Mapped[date] = mapped_column(nullable=False)
    photo_file_ids: Mapped[list[str]] = mapped_column(ARRAY(String()), nullable=True)
    video_file_ids: Mapped[list[str]] = mapped_column(ARRAY(String()), nullable=True)

    __table_args__ = (
        UniqueConstraint('id', name='unique_previous_concert'),
    )


# Таблица c данными о предстоящих концертах
class FutureConcertsOrm(Base):
    __tablename__ = "future_concerts"
    
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String())
    created_at: Mapped[date] = mapped_column(nullable=False)

    artist_info_text: Mapped[str] = mapped_column(String(), nullable=True)
    artist_info_photo_file_ids: Mapped[list[str]] = mapped_column(ARRAY(String()), nullable=True)
    artist_info_video_file_ids: Mapped[list[str]] = mapped_column(ARRAY(String()), nullable=True)

    platform_info_text: Mapped[str] = mapped_column(String(), nullable=True)
    platform_info_photo_file_ids: Mapped[list[str]] = mapped_column(ARRAY(String()), nullable=True)
    platform_info_video_file_ids: Mapped[list[str]] = mapped_column(ARRAY(String()), nullable=True)

    holding_time: Mapped[date] = mapped_column(nullable=False)
    ticket_price: Mapped[int] = mapped_column(Integer())

    __table_args__ = (
        UniqueConstraint('id', name='unique_future_concert'),
    )


# Таблица c данными о новостях команды
class TeamNewsOrm(Base):
    __tablename__ = "team_news"
    
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String())
    created_at: Mapped[date] = mapped_column(nullable=False)

    text: Mapped[str] = mapped_column(String(), nullable=True)
    photo_file_ids: Mapped[list[str]] = mapped_column(ARRAY(String()), nullable=True)
    video_file_ids: Mapped[list[str]] = mapped_column(ARRAY(String()), nullable=True)

    __table_args__ = (
        UniqueConstraint('id', name='unique_team_news_item'),
    )


# Таблица c эксклюзивными треками концерта
class ExclusiveTracksOrm(Base):
    __tablename__ = "exclusive_tracks"
    
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String())
    created_at: Mapped[date] = mapped_column(nullable=False)

    audio_file_id: Mapped[str] = mapped_column(String())
    audio_file_info: Mapped[str] = mapped_column(String())

    __table_args__ = (
        UniqueConstraint('id', name='unique_exclusive_track'),
    )