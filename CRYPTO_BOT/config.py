import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment")

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")  # optional, free tier works without
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))  # seconds