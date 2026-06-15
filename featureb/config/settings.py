from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    QDRANT_URL: str
    QDRANT_API_KEY: str

    OPENAI_API_KEY: str = ""

    GROQ_API_KEY: str

    # Redis Cache (NEW)
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()

