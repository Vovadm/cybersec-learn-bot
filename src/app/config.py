from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    token: str = ""
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "cybersec"
    db_user: str = "user"
    db_password: str = "pass"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:"
            f"{self.db_password}@"
            f"{self.db_host}:{self.db_port}/"
            f"{self.db_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
