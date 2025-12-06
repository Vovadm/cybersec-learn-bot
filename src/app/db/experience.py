from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from app.db.db import async_session
from app.db.models import User, Lesson, UserLesson


async def give_exp(telegram_id: str, username: str | None, lesson_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalars().first()

            if not user:
                user = User(telegram_id=telegram_id, username=username, experience=0)
                session.add(user)

                await session.flush()

            lesson = await session.get(Lesson, lesson_id)
            if not lesson:
                return False

            try:
                session.add(UserLesson(user_id=user.id, lesson_id=lesson_id))

                await session.execute(
                    update(User)
                    .where(User.id == user.id)
                    .values(experience=User.experience + lesson.exp)
                )

                return True

            except IntegrityError:
                await session.rollback()
                return False
