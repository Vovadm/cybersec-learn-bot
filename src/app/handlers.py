from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.future import select

from app.keyboards import lessons_keyboard, start_keyboard
from app.lessons import get_lesson
from app.states import LearnStates
from app.db.db import async_session
from app.db.models import User
from app.db.experience import give_exp

router = Router()


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("добро пожаловать", reply_markup=start_keyboard())


@router.message(F.text == "Изучать теорию")
async def choose_theory(message: Message, state: FSMContext):
    await state.set_state(LearnStates.choosing_lesson)

    await message.answer("Выберите урок:", reply_markup=lessons_keyboard())


@router.message(F.text == "Смотреть достижения")
async def view_achievements(message: Message):
    if message.from_user is None:
        return

    telegram_id = str(message.from_user.id)

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()

        if user is None:
            await message.answer("Вы ещё не начали обучение. Опыт: 0 🥲")
            return

        await message.answer(f"Ваш опыт: ⭐️ {user.experience}")


@router.message(F.text.contains("Вернуться"))
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Вы вернулись в главное меню.", reply_markup=start_keyboard())


@router.message(LearnStates.choosing_lesson)
async def lesson_selected(message: Message, state: FSMContext):
    if message.text is None:
        return

    if message.from_user is None:
        return

    lesson = get_lesson(message.text)

    if lesson is None:
        await message.answer("Такого урока нет. Выберите из списка.")
        return

    await message.answer(f"📘 *{lesson.name}*\n\n{lesson.data}", parse_mode="Markdown")

    await give_exp(
        telegram_id=str(message.from_user.id),
        username=message.from_user.username,
        lesson_id=lesson.id,
    )
