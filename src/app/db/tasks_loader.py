import json
from pathlib import Path
from typing import Union

from app.db.models import Task
from app.db.db import async_session

BASE_PATH = Path(__file__).parent
TASKS_PATH = BASE_PATH / "data" / "tasks.json"


async def load_tasks_from_json(file_path: Union[str, Path] = TASKS_PATH):
    file_path = Path(file_path)
    if not file_path.exists():
        return

    with open(file_path, "r", encoding="utf-8") as f:
        tasks_data = json.load(f)

    async with async_session() as session:
        for item in tasks_data:
            task_id = item.get("id")
            if task_id is None:
                continue

            existing = await session.get(Task, task_id)
            if existing:
                continue

            raw_correct = item.get("correctOption", 0)
            if isinstance(raw_correct, int) and raw_correct > 0:
                correct_index = raw_correct - 1
            else:
                correct_index = int(raw_correct)

            task = Task(
                id=task_id,
                lesson_id=item["lessonId"],
                name=item.get("name", "Вопрос"),
                options=json.dumps(item.get("options", []), ensure_ascii=False),
                correct_option=correct_index,
                exp=item.get("exp", 0),
                explanation=item.get("explanation", ""),
            )
            session.add(task)

        await session.commit()
