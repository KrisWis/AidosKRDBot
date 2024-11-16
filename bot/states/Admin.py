from aiogram.fsm.state import State, StatesGroup

'''Прошедшие концерты'''
class PreviousConcertsStates(StatesGroup):
    wait_name = State()

    wait_info = State()

'''/Прошедшие концерты/'''