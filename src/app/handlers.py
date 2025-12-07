from collections.abc import Sequence
from typing import List, cast
from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PollAnswer, InputPollOption, InputPollOptionUnion
from sqlalchemy.future import select

from app.keyboards import lessons_keyboard, start_keyboard
from app.lessons import get_lesson
from app.states import LearnStates
from app.db.db import async_session
from app.db.models import Task, User
from app.db.experience import give_exp
from app.tasks import (
    POLL_TASK_MAP,
    award_task_exp_if_needed,
    register_poll,
    unregister_poll,
)

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
    if message.text is None or message.from_user is None:
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

    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.lesson_id == lesson.id))
        tasks = result.scalars().all()

        for task in tasks:
            options = task.get_options_list()
            correct_index = int(task.correct_option or 0)
            poll_options: List[InputPollOptionUnion] = [
                InputPollOption(text=option) for option in options
            ]
            if message.bot is None:
                return
            sent = await message.bot.send_poll(
                chat_id=message.chat.id,
                question=task.name or "Вопрос",
                options=poll_options,
                is_anonymous=False,
                type="quiz",
                correct_option_id=correct_index,
            )

            if sent.poll:
                register_poll(sent.poll.id, task.id)


@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, bot: Bot):
    poll_id = poll_answer.poll_id
    user = poll_answer.user
    option_ids = poll_answer.option_ids

    task_id = POLL_TASK_MAP.get(poll_id)
    if task_id is None:
        return

    chosen = option_ids[0] if option_ids else None
    if chosen is None:
        return

    async with async_session() as session:
        task = await session.get(Task, task_id)
    if not task:
        unregister_poll(poll_id)
        return

    correct_index: int = int(cast(int, task.correct_option or 0))
    explanation: str = str(task.explanation or "")
    exp_amount: int = int(cast(int, task.exp or 0))

    user = poll_answer.user
    if not user:
        return

    if chosen == correct_index:
        awarded = await award_task_exp_if_needed(
            telegram_id=str(user.id),
            username=user.username,
            task_id=task_id,
        )

        if awarded:
            await bot.send_message(
                user.id, f"✅ Правильно! +{exp_amount} XP\n\n{explanation}"
            )
        else:
            await bot.send_message(
                user.id,
                "✅ Правильно, но вы уже получили опыт за эту задачу ранее.",
            )
    else:
        await bot.send_message(user.id, f"❌ Неверно.\n\n{explanation}")

    unregister_poll(poll_id)
