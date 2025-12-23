from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    token: str = ""
    database_url: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra="ignore"


settings = Settings()
