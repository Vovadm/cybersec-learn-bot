from sqlalchemy import Column, Integer, String, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db import Base
import json


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    experience = Column(Integer, default=0)

    lessons = relationship("UserLesson", back_populates="user")
    task_attempts = relationship("UserTaskAttempt", back_populates="user")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    data = Column(String(2000), nullable=False)
    exp = Column(Integer, default=10)

    users = relationship("UserLesson", back_populates="lesson")
    tasks = relationship("Task", back_populates="lesson")


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


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    options: Mapped[str] = mapped_column(Text, nullable=False)
    correct_option: Mapped[int] = mapped_column(Integer, nullable=False)
    exp: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    lesson = relationship("Lesson", back_populates="tasks")
    attempts = relationship("UserTaskAttempt", back_populates="task")

    def get_options_list(self) -> list[str]:
        try:
            return json.loads(self.options)
        except Exception:
            return []


class UserTaskAttempt(Base):
    __tablename__ = "user_task_attempts"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", name="unique_user_task"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    correct = Column(Integer, default=0)

    user = relationship("User", back_populates="task_attempts")
    task = relationship("Task", back_populates="attempts")
