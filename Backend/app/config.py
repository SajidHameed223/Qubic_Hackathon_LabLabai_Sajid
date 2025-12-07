from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from .env
    )
    
    # Database
    database_url: str = "postgresql://autopilot:autopilot@db:5432/autopilot"
    
    # Environment
    env: Optional[str] = "local"
    
    # Qubic Configuration
    qubic_wallet_identity: Optional[str] = None
    qubic_agent_seed: Optional[str] = None
    qubic_rpc_url: str = "https://rpc.qubic.org"
    
    # JWT Secret
    secret_key: str = "your-secret-key-change-this-in-production"
    
    # OpenAI
    openai_api_key: Optional[str] = None


settings = Settings()