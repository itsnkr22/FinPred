from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://mirofish:mirofish@db:5432/mirofish"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Zep Cloud
    zep_api_key: str = ""

    # App
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"

    # Simulation
    default_agent_count: int = 50
    default_tick_duration_ms: int = 2000
    max_simulation_ticks: int = 60

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
