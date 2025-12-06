from pydantic import BaseModel


class UserOut(BaseModel):
    telegram_id: str
    username: str | None = None
    experience: int

    class Config:
        orm_mode = True


class LessonOut(BaseModel):
    id: int
    name: str
    data: str
    exp: int

    class Config:
        orm_mode = True
