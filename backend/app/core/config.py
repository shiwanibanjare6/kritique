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

    DEBUG_SQL: bool = False

    REVIEW_MODEL: str = "openai/gpt-oss-120b"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    MAX_CONCURRENT_LLM_CALLS: int = 4
    MAX_PATCH_CHARS: int = 200000
    REVIEW_FILE_PATTERNS: str = (
        "*.lock,package-lock.json,pnpm-lock.yaml,yarn.lock,poetry.lock,uv.lock,*.lockb,"
        "*.min.js,*.min.css,*.map,*.png,*.jpg,*.jpeg,*.gif,*.webp,*.ico,*.pdf,*.svg,"
        "*.woff,*.woff2,*.ttf,*.eot,vendor/**,dist/**,build/**,generated/**"
    )
    SECURITY_SCORE_WEIGHT: float = 0.40
    STYLE_SCORE_WEIGHT: float = 0.25
    ARCHITECTURE_SCORE_WEIGHT: float = 0.35
    LLM_REQUEST_TIMEOUT_SECONDS: float = 60.0
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_BASE_SECONDS: float = 0.5
    LLM_RETRY_MAX_SECONDS: float = 8.0
    LLM_RETRY_JITTER_SECONDS: float = 0.25
    REVIEW_INPUT_USD_PER_MILLION: float = 0.15
    REVIEW_OUTPUT_USD_PER_MILLION: float = 0.60

    CORS_ORIGINS: str = "http://localhost:3000,https://kritique-three.vercel.app"

    model_config = SettingsConfigDict(

        env_file=".env",
        extra="ignore"

    )


settings = Settings()


def get_cors_origins() -> list[str]:
    return [origin.strip().rstrip("/") for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
