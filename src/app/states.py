from aiogram.fsm.state import State, StatesGroup


class LearnStates(StatesGroup):
    choosing_lesson = State()
