from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./outmate.db"
    planner_provider: str = "demo"
    max_accounts_per_run: int = 15
    cors_origins: str = "http://localhost:3000"
    model_name: str = "demo-structured-planner"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
