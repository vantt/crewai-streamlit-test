# src/config/config_manager.py
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import os

@dataclass
class AppConfig:
    """Application configuration class"""
    openai_api_key: str
    openai_api_base: Optional[str]
    model_name: str = "gpt-3.5-turbo"
    debug_mode: bool = False

class ConfigurationManager:
    @staticmethod
    def load_config() -> AppConfig:
        """Load configuration from environment variables"""
        load_dotenv()
        
        required_vars = ['OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return AppConfig(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            openai_api_base=os.getenv('OPENAI_API_BASE'),
            model_name=os.getenv('MODEL_NAME', 'gpt-3.5-turbo'),
            debug_mode=os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        )

    @staticmethod
    def validate_config(config: AppConfig) -> bool:
        """Validate configuration"""
        return bool(config.openai_api_key)