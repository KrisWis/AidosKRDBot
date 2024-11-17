from sqlalchemy import *
from database.models import UsersOrm, PreviousConcertsOrm
from database.db import Base, engine, async_session, date
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

# Создаём класс для ORM
class AsyncORM:
    # Метод для создания таблиц
    @staticmethod
    async def create_tables():

        async with engine.begin() as conn:
            engine.echo = False

            assert engine.url.database == 'test', 'Дропать прод запрещено'

            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            engine.echo = True


    '''UsersORM'''
    # Получение пользователя по id
    @staticmethod
    async def get_user(user_id: int) -> UsersOrm:
        async with async_session() as session:

            result = await session.get(UsersOrm, user_id)

            return result
        

    # Получение пользователей по параметрам
    @staticmethod
    async def get_users(period: str = None, geo: str = None) -> list[UsersOrm] | str:
        
        now = datetime.now()
        date = now - timedelta(weeks=100000)

        if period == 'day':
            date = now - timedelta(hours=1)

        if period == 'week':
            week = now - timedelta(weeks=1)
            date = week

        if period == 'month':
            month = now - timedelta(days=30)
            date = month
        
        async with async_session() as session:

            if geo:
                result = await session.execute(
                    select(UsersOrm)
                )
                users = result.scalars().all()

                stmt = select(UsersOrm.user_geo, func.count(UsersOrm.user_id)) \
                    .select_from(UsersOrm) \
                    .where(UsersOrm.user_reg_date >= date) \
                    .group_by(UsersOrm.user_geo) \
                    .order_by(func.count(UsersOrm.user_id).desc()) \
                    .limit(10) \
                    .distinct()

                result = await session.execute(stmt)
                name = result.all()

                count_geo = {}
                for country in name:
                    count_geo[country[0]] = int(country[1])

                msg = ''
                for i in count_geo:
                    msg += f'{i}: {count_geo[i]} ' \
                        f'({round(count_geo[i] / len(await AsyncORM.get_users(period=period)) * 100, 2)}%)'

                return msg if msg else 'Не обнаружено'

            else:
                result = await session.execute(
                    select(UsersOrm).where(UsersOrm.user_reg_date >= date))
                users = result.scalars().all()
                
                return users
            
        
    # Добавление пользователя в базу данных
    @staticmethod
    async def add_user(user_id: int, username: str, user_reg_date: date, user_geo: str, referer_id: int) -> bool:
        user = await AsyncORM.get_user(user_id=user_id)
        
        if not user:
            user = UsersOrm(user_id=user_id, username=username, user_reg_date=user_reg_date, user_geo=user_geo, referer_id=referer_id)

            async with async_session() as session:
                session.add(user)

                await session.commit() 
            return True
        else:
            return False
        
    '''/UsersORM/'''

    '''PreviousConcertsORM'''
    # Получение прошедшего концерта по id
    @staticmethod
    async def get_previous_concert_by_id(previous_concert_id: int) -> PreviousConcertsOrm:
        async with async_session() as session:

            result = await session.get(PreviousConcertsOrm, previous_concert_id)

            return result
        
    # Получение прошедшего концерта по названию
    @staticmethod
    async def get_previous_concert_by_name(name: str) -> PreviousConcertsOrm:
        async with async_session() as session:

            result = await session.execute(
                select(PreviousConcertsOrm).where(PreviousConcertsOrm.name == name))
            previous_concert = result.scalar()
            
            return previous_concert
        

    # Добавление прошедшего концерта в базу данных
    @staticmethod
    async def add_previous_concert(name: str, info_text: str, photo_file_ids: list[str] = [],
        video_file_ids: list[str] = []) -> bool:

        user = PreviousConcertsOrm(name=name, info_text=info_text, photo_file_ids=photo_file_ids,
        video_file_ids=video_file_ids)

        async with async_session() as session:
            session.add(user)

            await session.commit() 

        return True


    # Получение всех прошедших концертов
    @staticmethod
    async def get_previous_concerts() -> list[PreviousConcertsOrm]:
        
        async with async_session() as session:
            result = await session.execute(
                select(PreviousConcertsOrm))
            previous_concerts = result.scalars().all()
            
            return previous_concerts
        

    # Изменение информации о прошедшем концерте
    @staticmethod
    async def change_previousConcert_info(id: int, info_text: str,
        photo_file_ids: list[str] = [], video_file_ids: list[str] = []) -> bool:

        async with async_session() as session:
            result = await session.execute(select(PreviousConcertsOrm).where(PreviousConcertsOrm.id == id))
            previousConcert: PreviousConcertsOrm = result.scalar()

            previousConcert.info_text = info_text
            previousConcert.photo_file_ids = photo_file_ids
            previousConcert.video_file_ids = video_file_ids

            await session.commit()
                
        return True
    

    # Удаление прошедшего концерта по id
    @staticmethod
    async def delete_previous_concert(id: int) -> PreviousConcertsOrm:
        async with async_session() as session:

            result = await session.execute(select(PreviousConcertsOrm).where(PreviousConcertsOrm.id == id))
            previousConcert: PreviousConcertsOrm = result.scalar()
            
            if previousConcert:
                await session.delete(previousConcert)
                await session.commit()  
                return True
            
            return False

    '''/PreviousConcertsORM/'''