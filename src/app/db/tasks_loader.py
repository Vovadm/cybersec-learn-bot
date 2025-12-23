import json
from pathlib import Path
from typing import cast, Union

from app.db.db import async_session
from app.db.models import Task

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

            raw_correct = item.get("correctOption", [])

            if isinstance(raw_correct, int):
                correct_indices = [raw_correct - 1]

            elif isinstance(raw_correct, list):
                ints = cast(list[int], raw_correct)
                correct_indices = [i - 1 for i in ints]

            else:
                correct_indices = []

            task = Task(
                id=task_id,
                lesson_id=item["lessonId"],
                name=item.get("name", "Вопрос"),
                options=json.dumps(
                    item.get("options", []), ensure_ascii=False
                ),
                correct_options=json.dumps(
                    correct_indices, ensure_ascii=False
                ),
                exp=item.get("exp", 0),
                explanation=item.get("explanation", ""),
            )

            session.add(task)

        await session.commit()
