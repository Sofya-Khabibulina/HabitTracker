"""
Configuration settings for the Habit Tracker Bot
Loads environment variables and provides configuration objects
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        # Parse admin IDs from comma-separated string
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        self.ADMIN_IDS = []
        if admin_ids_str:
            try:
                self.ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
            except ValueError:
                raise ValueError("ADMIN_IDS must be comma-separated integers")
        
        # API Configuration
        self.QUOTE_API_URL = os.getenv("QUOTE_API_URL", "https://api.quotable.io/random")
        
        # File paths
        self.DATA_FILE_PATH = "storage/habits_data.json"
        self.LOG_FILE_PATH = "logs/habit_tracker.log"
        
        # Cache settings
        self.QUOTE_CACHE_DURATION = 12 * 60 * 60  # 12 hours in seconds
        
        # Throttling settings
        self.THROTTLE_RATE_LIMIT = 1  # seconds between messages per user

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
