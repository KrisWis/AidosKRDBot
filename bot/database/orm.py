from sqlalchemy import *
from database.models import UsersOrm, PreviousConcertsOrm, FutureConcertsOrm, TeamNewsOrm, ExclusiveTracksOrm, ConcertMusicOrm, RebatesOrm, StocksOrm
from database.db import Base, engine, async_session, date
from datetime import datetime, timedelta
from typing import Union

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
    async def get_all_users(period: str = None, geo: str = None) -> list[UsersOrm] | str:
        
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
                        f'({round(count_geo[i] / len(await AsyncORM.get_all_users(period=period)) * 100, 2)}%)'

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
    async def add_previous_concert(name: str, info_text: str, created_at: Date, photo_file_ids: list[str] = [],
        video_file_ids: list[str] = []) -> bool:

        previous_concert = PreviousConcertsOrm(name=name, info_text=info_text, created_at=created_at, photo_file_ids=photo_file_ids,
        video_file_ids=video_file_ids)

        async with async_session() as session:
            session.add(previous_concert)

            await session.commit() 

        return True


    # Получение всех прошедших концертов
    @staticmethod
    async def get_all_previous_concerts() -> list[PreviousConcertsOrm]:
        
        async with async_session() as session:
            result = await session.execute(
                select(PreviousConcertsOrm).order_by(PreviousConcertsOrm.created_at.desc()))
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

    '''FutureConcertsORM'''
    # Получение предстоящего концерта по id
    @staticmethod
    async def get_future_concert_by_id(id: int) -> FutureConcertsOrm:
        async with async_session() as session:

            result = await session.execute(
                select(FutureConcertsOrm).where(FutureConcertsOrm.id == id))
            future_concert = result.scalar()
            
            return future_concert
        

    # Получение предстоящего концерта по названию
    @staticmethod
    async def get_future_concert_by_name(name: str) -> FutureConcertsOrm:
        async with async_session() as session:

            result = await session.execute(
                select(FutureConcertsOrm).where(FutureConcertsOrm.name == name))
            future_concert = result.scalar()
            
            return future_concert
        
        
    # Получение информации об артисте предстоящего концерта по id концерта
    @staticmethod
    async def get_future_concert_artist_info_by_id(future_concert_id: int) -> Union[str, list[str], list[str]]:
        async with async_session() as session:

            result: FutureConcertsOrm = await session.get(FutureConcertsOrm, future_concert_id)
            
            if result:
                return [result.artist_info_text, result.artist_info_photo_file_ids, result.artist_info_video_file_ids]
            
            return False
        

    # Получение информации о площадке предстоящего концерта по id концерта
    @staticmethod
    async def get_future_concert_platform_info_by_id(future_concert_id: int) -> Union[str, list[str], list[str]]:
        async with async_session() as session:

            result: FutureConcertsOrm = await session.get(FutureConcertsOrm, future_concert_id)
            
            if result:
                return [result.platform_info_text, result.platform_info_photo_file_ids, result.platform_info_video_file_ids]
            
            return False
        

    # Получение информации о времени проведения предстоящего концерта по id концерта
    @staticmethod
    async def get_future_concert_holding_time_by_id(future_concert_id: int) -> date:
        async with async_session() as session:

            result: FutureConcertsOrm = await session.get(FutureConcertsOrm, future_concert_id)

            return result.holding_time
        

    # Получение информации о стоимость билета предстоящего концерта по id концерта
    @staticmethod
    async def get_future_concert_ticket_price_by_id(future_concert_id: int) -> int:
        async with async_session() as session:

            result: FutureConcertsOrm = await session.get(FutureConcertsOrm, future_concert_id)

            return result.ticket_price
        

    # Добавление предстоящего концерта в базу данных
    @staticmethod
    async def add_future_concert(name: str, created_at: Date, artist_info_text: str,
        platform_info_text: str, holding_time: Date, ticket_price: int, artist_info_photo_file_ids: list[str] = [],
        artist_info_video_file_ids: list[str] = [],
        platform_info_photo_file_ids: list[str] = [],
        platform_info_video_file_ids: list[str] = []) -> bool:

        future_concert = FutureConcertsOrm(name=name, created_at=created_at, artist_info_text=artist_info_text,
        artist_info_photo_file_ids=artist_info_photo_file_ids, artist_info_video_file_ids=artist_info_video_file_ids,
        platform_info_photo_file_ids=platform_info_photo_file_ids, platform_info_video_file_ids=platform_info_video_file_ids,
        platform_info_text=platform_info_text, holding_time=holding_time, ticket_price=ticket_price)

        async with async_session() as session:
            session.add(future_concert)

            await session.commit() 

        return True


    # Получение всех предстоящих концертов
    @staticmethod
    async def get_all_future_concerts() -> list[FutureConcertsOrm]:
        
        async with async_session() as session:
            result = await session.execute(
                select(FutureConcertsOrm).order_by(FutureConcertsOrm.holding_time.asc()))
            future_concerts = result.scalars().all()
            
            return future_concerts
        

    # Изменение информации об артисте предстоящего концерта по id концерта
    @staticmethod
    async def change_futureConcert_artist_info(id: int, artist_info_text: str,
        photo_file_ids: list[str], video_file_ids: list[str]) -> bool:

        async with async_session() as session:
            result = await session.execute(select(FutureConcertsOrm).where(FutureConcertsOrm.id == id))
            futureConcert: FutureConcertsOrm = result.scalar()

            futureConcert.artist_info_text = artist_info_text
            futureConcert.artist_info_photo_file_ids = photo_file_ids
            futureConcert.artist_info_video_file_ids = video_file_ids

            await session.commit()
                
        return True
    

    # Изменение информации о площадке предстоящего концерта по id концерта
    @staticmethod
    async def change_futureConcert_platform_info(id: int, platform_info_text: str,
        photo_file_ids: list[str], video_file_ids: list[str]) -> bool:

        async with async_session() as session:
            result = await session.execute(select(FutureConcertsOrm).where(FutureConcertsOrm.id == id))
            futureConcert: FutureConcertsOrm = result.scalar()

            futureConcert.platform_info_text = platform_info_text
            futureConcert.platform_info_photo_file_ids = photo_file_ids
            futureConcert.platform_info_video_file_ids = video_file_ids

            await session.commit()
                
        return True
    

    # Изменение информации о времени проведения предстоящего концерта по id концерта
    @staticmethod
    async def change_futureConcert_holding_time(id: int, holding_time: date) -> bool:

        async with async_session() as session:
            result = await session.execute(select(FutureConcertsOrm).where(FutureConcertsOrm.id == id))
            futureConcert: FutureConcertsOrm = result.scalar()

            futureConcert.holding_time = holding_time

            await session.commit()
                
        return True
    

    # Изменение информации о стоимости билета предстоящего концерта по id концерта
    @staticmethod
    async def change_futureConcert_ticket_price(id: int, ticket_price: int) -> bool:

        async with async_session() as session:
            result = await session.execute(select(FutureConcertsOrm).where(FutureConcertsOrm.id == id))
            futureConcert: FutureConcertsOrm = result.scalar()

            futureConcert.ticket_price = ticket_price

            await session.commit()
                
        return True
    

    # Удаление предстоящего концерта по id
    @staticmethod
    async def delete_future_concert(id: int) -> FutureConcertsOrm:
        async with async_session() as session:

            result = await session.execute(select(FutureConcertsOrm).where(FutureConcertsOrm.id == id))
            futureConcert: FutureConcertsOrm = result.scalar()
            
            if futureConcert:
                await session.delete(futureConcert)
                await session.commit()  
                return True
            
            return False
    '''/FutureConcertsORM/'''


    '''TeamNewsORM'''
    # Получение новости по id
    @staticmethod
    async def get_team_news_item_by_id(id: int) -> TeamNewsOrm:
        async with async_session() as session:

            result = await session.execute(
                select(TeamNewsOrm).where(TeamNewsOrm.id == id))
            news_item = result.scalar()
            
            return news_item
        

    # Получение новости по названию
    @staticmethod
    async def get_team_news_item_by_name(name: str) -> TeamNewsOrm:
        async with async_session() as session:

            result = await session.execute(
                select(TeamNewsOrm).where(TeamNewsOrm.name == name))
            news_item = result.scalar()
            
            return news_item
        

    # Добавление новости в базу данных
    @staticmethod
    async def add_team_news_item(name: str, created_at: Date, text: str,
        photo_file_ids: list[str] = [],
        video_file_ids: list[str] = []) -> bool:

        news_item = TeamNewsOrm(name=name, created_at=created_at, text=text,
        photo_file_ids=photo_file_ids, video_file_ids=video_file_ids)

        async with async_session() as session:
            session.add(news_item)

            await session.commit() 

        return True


    # Получение всех новостей команды
    @staticmethod
    async def get_all_team_news() -> list[TeamNewsOrm]:
        
        async with async_session() as session:
            result = await session.execute(
                select(TeamNewsOrm).order_by(TeamNewsOrm.created_at.desc()))
            team_news = result.scalars().all()
            
            return team_news
        

    # Изменение информации новости команды
    @staticmethod
    async def change_team_news_item_info(id: int, text: str,
        photo_file_ids: list[str], video_file_ids: list[str]) -> bool:

        async with async_session() as session:
            result = await session.execute(select(TeamNewsOrm).where(TeamNewsOrm.id == id))
            news_item: TeamNewsOrm = result.scalar()

            news_item.text = text
            news_item.photo_file_ids = photo_file_ids
            news_item.video_file_ids = video_file_ids

            await session.commit()
                
        return True
    

    # Удаление новости команды по id
    @staticmethod
    async def delete_team_news_item(id: int) -> TeamNewsOrm:
        async with async_session() as session:

            result = await session.execute(select(TeamNewsOrm).where(TeamNewsOrm.id == id))
            news_item: TeamNewsOrm = result.scalar()
            
            if news_item:
                await session.delete(news_item)
                await session.commit()  
                return True
            
            return False
    '''/TeamNewsORM/'''


    '''ExclusiveTracksOrm'''
    # Получение эксклюзивного трека по id
    @staticmethod
    async def get_exclusive_track_by_id(id: int) -> ExclusiveTracksOrm:
        async with async_session() as session:

            result = await session.execute(
                select(ExclusiveTracksOrm).where(ExclusiveTracksOrm.id == id))
            exclusive_track = result.scalar()
            
            return exclusive_track
        

    # Получение эксклюзивного трека по названию
    @staticmethod
    async def get_exclusive_track_by_name(name: str) -> ExclusiveTracksOrm:
        async with async_session() as session:

            result = await session.execute(
                select(ExclusiveTracksOrm).where(ExclusiveTracksOrm.name == name))
            exclusive_track = result.scalar()
            
            return exclusive_track
        

    # Добавление эксклюзивного трека в базу данных
    @staticmethod
    async def add_exclusive_track(name: str, created_at: Date, audio_file_id: str,
    audio_file_info: str) -> bool:

        exclusive_track = ExclusiveTracksOrm(name=name, created_at=created_at,
        audio_file_id=audio_file_id, audio_file_info=audio_file_info)

        async with async_session() as session:
            session.add(exclusive_track)

            await session.commit() 

        return True


    # Получение всех эксклюзивных треков
    @staticmethod
    async def get_all_exclusive_tracks() -> list[ExclusiveTracksOrm]:
        
        async with async_session() as session:
            result = await session.execute(
                select(ExclusiveTracksOrm).order_by(ExclusiveTracksOrm.created_at.desc()))
            exclusive_tracks = result.scalars().all()
            
            return exclusive_tracks
        

    # Изменение эксклюзивного трека
    @staticmethod
    async def change_exclusive_track(id: int, audio_file_id: str,
    audio_file_info: str) -> bool:

        async with async_session() as session:
            result = await session.execute(select(ExclusiveTracksOrm)
            .where(ExclusiveTracksOrm.id == id))
            exclusive_track: ExclusiveTracksOrm = result.scalar()

            exclusive_track.audio_file_id = audio_file_id
            exclusive_track.audio_file_info = audio_file_info

            await session.commit()
                
        return True
    

    # Удаление эксклюзивного трека по id
    @staticmethod
    async def delete_exclusive_track(id: int) -> ExclusiveTracksOrm:
        async with async_session() as session:

            result = await session.execute(select(ExclusiveTracksOrm)
            .where(ExclusiveTracksOrm.id == id))
            exclusive_track: ExclusiveTracksOrm = result.scalar()
            
            if exclusive_track:
                await session.delete(exclusive_track)
                await session.commit()  
                return True
            
            return False
    '''/ExclusiveTracksOrm/'''


    '''ConcertMusicOrm'''
    # Получение музыки с концерта по id
    @staticmethod
    async def get_concert_music_item_by_id(id: int) -> ConcertMusicOrm:
        async with async_session() as session:

            result = await session.execute(
                select(ConcertMusicOrm).where(ConcertMusicOrm.id == id))
            concert_music = result.scalar()
            
            return concert_music
        

    # Получение музыки с концерта по названию
    @staticmethod
    async def get_concert_music_item_by_name(name: str) -> ConcertMusicOrm:
        async with async_session() as session:

            result = await session.execute(
                select(ConcertMusicOrm).where(ConcertMusicOrm.name == name))
            concert_music = result.scalar()
            
            return concert_music
        

    # Добавление музыки с концерта в базу данных
    @staticmethod
    async def add_concert_music_item(name: str, created_at: Date, audio_file_id: str,
    audio_file_info: str) -> bool:

        concert_music = ConcertMusicOrm(name=name, created_at=created_at,
        audio_file_id=audio_file_id, audio_file_info=audio_file_info)

        async with async_session() as session:
            session.add(concert_music)

            await session.commit() 

        return True


    # Получение всей музыки с концерта
    @staticmethod
    async def get_all_concert_music() -> list[ConcertMusicOrm]:
        
        async with async_session() as session:
            result = await session.execute(
                select(ConcertMusicOrm).order_by(ConcertMusicOrm.created_at.desc()))
            concert_music = result.scalars().all()
            
            return concert_music
        

    # Изменение музыки с концерта
    @staticmethod
    async def change_concert_music_item(id: int, audio_file_id: str,
    audio_file_info: str) -> bool:

        async with async_session() as session:
            result = await session.execute(select(ConcertMusicOrm)
            .where(ConcertMusicOrm.id == id))
            concert_music: ConcertMusicOrm = result.scalar()

            concert_music.audio_file_id = audio_file_id
            concert_music.audio_file_info = audio_file_info

            await session.commit()
                
        return True
    

    # Удаление музыки с концерта по id
    @staticmethod
    async def delete_concert_music_item(id: int) -> ConcertMusicOrm:
        async with async_session() as session:

            result = await session.execute(select(ConcertMusicOrm)
            .where(ConcertMusicOrm.id == id))
            concert_music: ConcertMusicOrm = result.scalar()
            
            if concert_music:
                await session.delete(concert_music)
                await session.commit()  
                return True
            
            return False
    '''/ConcertMusicOrm/'''


    '''RebatesOrm'''
    # Получение скидки по id
    @staticmethod
    async def get_rebate_by_id(id: int) -> RebatesOrm:
        async with async_session() as session:

            result = await session.execute(
                select(RebatesOrm).where(RebatesOrm.id == id))
            rebate = result.scalar()
            
            return rebate
        

    # Получение скидки по названию
    @staticmethod
    async def get_rebate_by_name(name: str) -> RebatesOrm:
        async with async_session() as session:

            result = await session.execute(
                select(RebatesOrm).where(RebatesOrm.name == name))
            rebate = result.scalar()
            
            return rebate
        

    # Добавление скидки в базу данных
    @staticmethod
    async def add_rebate(name: str, created_at: Date, text: str,
        photo_file_ids: list[str] = [],
        video_file_ids: list[str] = []) -> bool:

        rebate = RebatesOrm(name=name, created_at=created_at, text=text,
        photo_file_ids=photo_file_ids, video_file_ids=video_file_ids)

        async with async_session() as session:
            session.add(rebate)

            await session.commit() 

        return True


    # Получение всех скидок
    @staticmethod
    async def get_all_rebates() -> list[RebatesOrm]:
        
        async with async_session() as session:
            result = await session.execute(
                select(RebatesOrm).order_by(RebatesOrm.created_at.desc()))
            rebate = result.scalars().all()
            
            return rebate
        

    # Изменение информации о скидке
    @staticmethod
    async def change_rebate_info(id: int, text: str,
        photo_file_ids: list[str], video_file_ids: list[str]) -> bool:

        async with async_session() as session:
            result = await session.execute(select(RebatesOrm).where(RebatesOrm.id == id))
            rebate: RebatesOrm = result.scalar()

            rebate.text = text
            rebate.photo_file_ids = photo_file_ids
            rebate.video_file_ids = video_file_ids

            await session.commit()
                
        return True
    

    # Удаление скидки по id
    @staticmethod
    async def delete_rebate(id: int) -> RebatesOrm:
        async with async_session() as session:

            result = await session.execute(select(RebatesOrm).where(RebatesOrm.id == id))
            rebate: RebatesOrm = result.scalar()
            
            if rebate:
                await session.delete(rebate)
                await session.commit()  
                return True
            
            return False
    '''/RebatesOrm/'''


    '''StocksOrm'''
    # Получение акции по id
    @staticmethod
    async def get_stock_by_id(id: int) -> StocksOrm:
        async with async_session() as session:

            result = await session.execute(
                select(StocksOrm).where(StocksOrm.id == id))
            stock = result.scalar()
            
            return stock
        

    # Получение акции по названию
    @staticmethod
    async def get_stock_by_name(name: str) -> StocksOrm:
        async with async_session() as session:

            result = await session.execute(
                select(StocksOrm).where(StocksOrm.name == name))
            stock = result.scalar()
            
            return stock
        

    # Добавление акции в базу данных
    @staticmethod
    async def add_stock(name: str, created_at: Date, text: str,
        photo_file_ids: list[str] = [],
        video_file_ids: list[str] = []) -> bool:

        stock = StocksOrm(name=name, created_at=created_at, text=text,
        photo_file_ids=photo_file_ids, video_file_ids=video_file_ids)

        async with async_session() as session:
            session.add(stock)

            await session.commit() 

        return True


    # Получение всех акций
    @staticmethod
    async def get_all_stocks() -> list[StocksOrm]:
        
        async with async_session() as session:
            result = await session.execute(
                select(StocksOrm).order_by(StocksOrm.created_at.desc()))
            stock = result.scalars().all()
            
            return stock
        

    # Изменение информации об акции
    @staticmethod
    async def change_stock_info(id: int, text: str,
        photo_file_ids: list[str], video_file_ids: list[str]) -> bool:

        async with async_session() as session:
            result = await session.execute(select(StocksOrm).where(StocksOrm.id == id))
            stock: StocksOrm = result.scalar()

            stock.text = text
            stock.photo_file_ids = photo_file_ids
            stock.video_file_ids = video_file_ids

            await session.commit()
                
        return True
    

    # Удаление акции по id
    @staticmethod
    async def delete_stock(id: int) -> StocksOrm:
        async with async_session() as session:

            result = await session.execute(select(StocksOrm).where(StocksOrm.id == id))
            stock: StocksOrm = result.scalar()
            
            if stock:
                await session.delete(stock)
                await session.commit()  
                return True
            
            return False
    '''/StocksOrm/'''