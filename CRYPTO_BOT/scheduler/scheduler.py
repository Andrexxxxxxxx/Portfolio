import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone
from sqlalchemy import select
from database import AsyncSessionLocal
from database.models import User, MonitoredCoin
from services.price_service import PriceService
from services.notification_service import NotificationService
from bot import bot
from config import CHECK_INTERVAL

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_prices():
    """Background job to check prices for all monitored coins."""
    logger.info("Starting price check job")
    try:
        async with AsyncSessionLocal() as session:
            # Load all monitored coins with user data
            result = await session.execute(
                select(MonitoredCoin).join(User).where(User.notifications_enabled == True)
            )
            monitored = result.scalars().all()

            if not monitored:
                logger.info("No monitored coins found")
                return

            # Group by coin_id to fetch once
            coin_ids = list({m.coin_id for m in monitored})
            async with PriceService() as price_svc:
                prices = await price_svc.get_prices(coin_ids)

            if not prices:
                logger.warning("No prices received from API")
                return

            # Process each monitored coin
            notification_svc = NotificationService(bot)
            for coin in monitored:
                if coin.coin_id not in prices:
                    continue
                new_price = prices[coin.coin_id]
                old_price = coin.last_price
                if old_price is None:
                    # First time, just update
                    coin.last_price = new_price
                    coin.last_updated = datetime.now(timezone.utc)
                    continue

                # Calculate percentage change
                if old_price == 0:
                    continue
                change = ((new_price - old_price) / old_price) * 100
                if abs(change) >= coin.user.threshold:
                    # Send alert
                    await notification_svc.send_alert(
                        user_telegram_id=coin.user.telegram_id,
                        coin_name=coin.coin_id.capitalize(),  # could store name too
                        symbol=coin.symbol.upper(),
                        old_price=old_price,
                        new_price=new_price,
                        change_percent=change
                    )
                # Update price regardless
                coin.last_price = new_price
                coin.last_updated = datetime.now(timezone.utc)

            await session.commit()
            logger.info(f"Price check completed, processed {len(monitored)} coins")

    except Exception as e:
        logger.error(f"Error in price check job: {e}", exc_info=True)

def setup_scheduler():
    """Configure and start the scheduler."""
    scheduler.add_job(
        check_prices,
        trigger=IntervalTrigger(seconds=CHECK_INTERVAL),
        id="price_check",
        replace_existing=True,
        coalesce=True
    )
    scheduler.start()
    logger.info(f"Scheduler started, interval = {CHECK_INTERVAL} seconds")
