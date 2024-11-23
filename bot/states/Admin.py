from aiogram.fsm.state import State, StatesGroup

'''Прошедшие концерты'''
class PreviousConcertsStates(StatesGroup):
    wait_name = State()

    wait_info = State()
'''/Прошедшие концерты/'''


'''Предстоящие концерты'''
class FutureConcertsStates(StatesGroup):
    wait_name = State()
    
    wait_artist_info = State()

    wait_platform_info = State()

    wait_holding_time = State()

    wait_ticket_price = State()
'''/Предстоящие концерты/'''

'''Что нового?'''
class WhatIsNewStates(StatesGroup):
    '''Новости команды'''
    team_news_item_wait_name = State()

    team_news_item_wait_info = State()
    '''/Новости команды/'''

    '''Эксклюзивные треки'''
    exclusive_track_wait_name = State()

    exclusive_track_wait_info = State()
    '''/Эксклюзивные треки/'''

    '''Музыка с концерта'''
    concert_music_item_wait_name = State()

    concert_music_item_wait_info = State()
    '''/Музыка с концерта/'''
'''/Что нового?/'''