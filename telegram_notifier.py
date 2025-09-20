import requests
from typing import Optional
from config import Config

API_URL = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"

def send_message(text: str, parse_mode: Optional[str] = None) -> None:
    payload = {
        "chat_id": Config.TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    resp = requests.post(API_URL, json=payload, timeout=10)
    resp.raise_for_status()
