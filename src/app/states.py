from aiogram.fsm.state import StatesGroup, State


class LearnStates(StatesGroup):
    choosing_lesson = State()
