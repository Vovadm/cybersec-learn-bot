from pydantic import BaseModel


class UserSchema(BaseModel):
    telegram_id: str
    username: str | None = None
    experience: int = 0

    class Config:
        orm_mode = True


class LessonSchema(BaseModel):
    id: int
    name: str
    data: str
    exp: int

    class Config:
        orm_mode = True
