import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_host: str = os.getenv("DATABASE_HOST", "localhost")
    database_port: int = int(os.getenv("DATABASE_PORT", "5432"))
    database_name: str = os.getenv("DATABASE_NAME", "distributed_tasks")
    database_user: str = os.getenv("DATABASE_USER", "postgres")
    database_password: str = os.getenv("DATABASE_PASSWORD", "")

    @property
    def database_url(self) -> str:
        return (
            f"host={self.database_host} port={self.database_port} "
            f"dbname={self.database_name} user={self.database_user} "
            f"password={self.database_password}"
        )


settings = Settings()