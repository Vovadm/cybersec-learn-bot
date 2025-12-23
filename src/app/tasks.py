from typing import Dict

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.db.db import async_session
from app.db.models import Task, User, UserTaskAttempt


POLL_TASK_MAP: Dict[str, int] = {}


def register_poll(poll_id: str, task_id: int):
    POLL_TASK_MAP[poll_id] = task_id


def unregister_poll(poll_id: str):
    POLL_TASK_MAP.pop(poll_id, None)


async def award_task_exp_if_needed(
    telegram_id: str, username: str | None, task_id: int
) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()
        if not user:
            user = User(
                telegram_id=telegram_id, username=username, experience=0
            )
            session.add(user)
            await session.flush()

        task = await session.get(Task, task_id)
        if not task:
            return False

        existing = await session.execute(
            select(UserTaskAttempt).where(
                UserTaskAttempt.user_id == user.id,
                UserTaskAttempt.task_id == task_id,
            )
        )
        if existing.scalars().first():
            return False

        try:
            attempt = UserTaskAttempt(
                user_id=user.id, task_id=task_id, correct=1
            )
            session.add(attempt)

            await session.execute(
                update(User)
                .where(User.id == user.id)
                .values(experience=User.experience + (task.exp or 0))
            )
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False
