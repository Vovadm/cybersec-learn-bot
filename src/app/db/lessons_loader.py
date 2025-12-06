import json
from app.db.models import Lesson
from app.db.db import async_session


async def load_lessons_from_json(file_path: str):
    async with async_session() as session:
        with open(file_path, "r", encoding="utf-8") as f:
            lessons_data = json.load(f)

        for i in lessons_data:

            lesson = await session.get(Lesson, i["id"])
            if not lesson:
                lesson = Lesson(
                    id=i["id"],
                    name=i["name"],
                    data=i["data"],
                    exp=i.get("exp", 10),
                )
                session.add(lesson)

        await session.commit()
