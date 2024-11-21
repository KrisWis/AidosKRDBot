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
    wait_name = State()

    wait_info = State()
'''/Что нового?/'''