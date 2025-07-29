import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Configuration settings with environment variable support."""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Groww API Configuration (OAuth 2.0 Token-based)
    groww_api_token: Optional[str] = None
    
    # Trading Configuration (percentages converted to decimals)
    max_investment_amount: float = 50000.0
    risk_threshold: float = 15.0  # 15% as percentage
    min_expected_return_pct: float = Field(default=15.0, alias='MIN_EXPECTED_RETURN')  # 15% as percentage  
    expected_return_days: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def min_expected_return(self) -> float:
        """Convert percentage to decimal (15.0% -> 0.15)"""
        return self.min_expected_return_pct / 100.0
    
    @property
    def risk_threshold_decimal(self) -> float:
        """Convert risk threshold percentage to decimal"""
        return self.risk_threshold / 100.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

# Global settings instance
settings = get_settings() 