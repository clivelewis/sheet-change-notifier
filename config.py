import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Google credentials: path to service account key JSON
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")

    # What to watch
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
    WORKSHEET_NAME = os.getenv("WORKSHEET_NAME", "Sheet1")
    CELL = os.getenv("CELL", "A1")

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # Polling
    POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

    # State persistence
    STATE_FILE = os.getenv("STATE_FILE", "state.json")
    
    # Cells configuration
    CELLS_CONFIG_FILE = os.getenv("CELLS_CONFIG_FILE", "cells_config.json")

    # Basic validation
    @classmethod
    def validate(cls):
        missing = []
        for key in ("SPREADSHEET_ID", "WORKSHEET_NAME", "CELL",
                    "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
            if not getattr(cls, key):
                missing.append(key)
        if missing:
            raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")
