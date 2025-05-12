from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    project_base_dir: Path = Path(__file__).parent.parent
    base_dir: Path = project_base_dir.parent.parent
    data_dir: Path = base_dir / "data"


settings = Settings()
