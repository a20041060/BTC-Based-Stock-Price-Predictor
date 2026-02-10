from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """
    Application configuration using Pydantic Settings.
    Reads from environment variables and .env file.
    """
    APP_NAME: str = "BTC Stock Predictor"
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # API Keys
    FINNHUB_API_KEY: Optional[str] = Field(default=None, description="Finnhub API Key for stock data")
    X_API_BEARER_TOKEN: Optional[str] = Field(default=None, description="X (Twitter) API Bearer Token")
    
    # Model Configuration
    USE_TRANSFORMERS: bool = Field(default=True, description="Whether to use HuggingFace Transformers")
    TRANSFORMER_MODEL: str = "ProsusAI/finbert"
    
    # Data Fetching
    BINANCE_BTC_URL: str = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
