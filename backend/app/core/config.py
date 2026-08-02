from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str

    APP_VERSION: str

    DEBUG: bool

    HOST: str

    PORT: int

    GITHUB_SECRET: str

    GITHUB_TOKEN: str

    DATABASE_URL: str

    GROQ_API_KEY: str

    REDIS_URL: str = ""

    model_config = SettingsConfigDict(

        env_file=".env",

        extra="ignore"

    )


settings = Settings()