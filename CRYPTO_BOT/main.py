import asyncio
import logging
from bot import dp, bot
from database import init_db
from scheduler.scheduler import setup_scheduler
from handlers import commands  # noqa: register handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def on_startup():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Setting up scheduler...")
    setup_scheduler()

async def main():
    await on_startup()
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
