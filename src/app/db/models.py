from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    experience = Column(Integer, default=0)

    lessons = relationship("UserLesson", back_populates="user")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    data = Column(String(2000), nullable=False)
    exp = Column(Integer, default=10)

    users = relationship("UserLesson", back_populates="lesson")


class UserLesson(Base):
    __tablename__ = "user_lessons"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="unique_user_lesson"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))

    user = relationship("User", back_populates="lessons")
    lesson = relationship("Lesson", back_populates="users")
