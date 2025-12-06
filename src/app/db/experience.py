from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.db.db import async_session
from app.db.models import User, Lesson, UserLesson


async def give_exp(telegram_id: str, username: str | None, lesson_id: int):
    async with async_session() as session:

        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()
        if not user:
            user = User(telegram_id=telegram_id, username=username, experience=0)
            session.add(user)
            await session.commit()

        try:
            user_lesson = UserLesson(user_id=user.id, lesson_id=lesson_id)
            session.add(user_lesson)

            lesson = await session.get(Lesson, lesson_id)
            if lesson:
                user.experience = user.experience + lesson.exp  # type: ignore
            await session.commit()
        except IntegrityError:

            await session.rollback()
