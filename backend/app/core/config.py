from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR.joinpath(".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Deepseek配置
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-flash"

    # ── DashScope（Embedding） ──
    dashscope_api_key: str
    dashscope_base_url: str
    dashscope_embedding_model: str = "text-embedding-v4"
    embedding_dimensions: int = 1024

    # Langfuse配置
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_base_url: str

    # ── 应用 ──
    app_env: str = "development"
    log_level: str = "INFO"


settings = Settings()
