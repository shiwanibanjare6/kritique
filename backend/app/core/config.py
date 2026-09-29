from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str

    APP_VERSION: str

    DEBUG: bool

    HOST: str

    PORT: int

    GITHUB_SECRET: str

    GITHUB_TOKEN: str = ""

    DATABASE_URL: str

    GROQ_API_KEY: str

    REDIS_URL: str = ""

    CORS_ORIGINS: str = "http://localhost:3000,https://kritique-three.vercel.app"

    model_config = SettingsConfigDict(

        env_file=".env",
        extra="ignore"

    )


settings = Settings()


def get_cors_origins() -> list[str]:
    return [origin.strip().rstrip("/") for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
