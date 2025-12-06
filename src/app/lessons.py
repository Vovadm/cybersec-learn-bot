import json
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent
LESSONS_PATH = BASE_PATH / "data" / "lessons.json"


class Lesson:
    def __init__(self, id: int, name: str, data: str, exp: int):
        self.id = id
        self.name = name
        self.data = data
        self.exp = exp


def load_lessons() -> list[Lesson]:
    with open(LESSONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [Lesson(**item) for item in data]


lessons = load_lessons()


def get_lesson(name: str):
    for lesson in lessons:
        if lesson.name == name:
            return lesson
    return None
