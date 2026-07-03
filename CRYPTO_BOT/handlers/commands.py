cat > handlers/commands.py << 'EOF'
import logging
from datetime import datetime, timezone
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, Update
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from database import AsyncSessionLocal
from database.models import User, MonitoredCoin
from services.price_service import PriceService
from bot import dp, bot

logger = logging.getLogger(__name__)

async def get_or_create_user(telegram_id: int, username: str = None) -> User:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
            except IntegrityError:
                await session.rollback()
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
        else:
            if username and user.username != username:
                user.username = username
                await session.commit()
        return user

@dp.message(Command("start"))
async def start_command(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.username)
    # FIXED: No HTML tags at all - using plain text with emojis only
    welcome = (
        "🚀 Welcome to Crypto Price Alert Bot!\n\n"
        "I monitor cryptocurrency prices and notify you when they change significantly.\n"
        "Set your own alert threshold and manage your watchlist.\n\n"
        "Commands:\n"
        "/add coin - add coin to monitor (e.g. /add BTC)\n"
        "/remove coin - remove coin\n"
        "/list - show monitored coins\n"
        "/price coin - get current price\n"
        "/threshold percent - set alert threshold (e.g. /threshold 3)\n"
        "/notifications on/off - enable/disable alerts\n"
        "/help - show this message"
    )
    await message.answer(welcome)

@dp.message(Command("help"))
async def help_command(message: Message):
    await start_command(message)

@dp.message(Command("add"))
async def add_coin(message: Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Please provide a coin symbol or name. Example: /add BTC")
        return

    user = await get_or_create_user(message.from_user.id, message.from_user.username)

    async with PriceService() as price_svc:
        coin_info = await price_svc.search_coin(query)
    if not coin_info:
        await message.answer(f"Coin '{query}' not found. Please check and try again.")
        return

    coin_id = coin_info["id"]
    symbol = coin_info["symbol"].upper()

    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(MonitoredCoin).where(
                MonitoredCoin.user_id == user.id,
                MonitoredCoin.coin_id == coin_id
            )
        )
        if existing.scalar_one_or_none():
            await message.answer(f"⚠️ {symbol} is already in your watchlist.")
            return

        new_coin = MonitoredCoin(
            user_id=user.id,
            coin_id=coin_id,
            symbol=symbol,
        )
        session.add(new_coin)
        try:
            await session.commit()
            async with PriceService() as price_svc:
                prices = await price_svc.get_prices([coin_id])
            if coin_id in prices:
                new_coin.last_price = prices[coin_id]
                new_coin.last_updated = datetime.now(timezone.utc)
                await session.commit()
            await message.answer(f"✅ Added {coin_info['name']} ({symbol}) to your watchlist.")
        except IntegrityError:
            await session.rollback()
            await message.answer("This coin is already in your watchlist.")
        except Exception as e:
            logger.error(f"Error adding coin: {e}")
            await message.answer("Failed to add coin. Please try again later.")

@dp.message(Command("remove"))
async def remove_coin(message: Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Please provide a coin symbol or name. Example: /remove BTC")
        return

    user = await get_or_create_user(message.from_user.id, message.from_user.username)

    async with PriceService() as price_svc:
        coin_info = await price_svc.search_coin(query)
    if not coin_info:
        await message.answer(f"Coin '{query}' not found.")
        return
    coin_id = coin_info["id"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MonitoredCoin).where(
                MonitoredCoin.user_id == user.id,
                MonitoredCoin.coin_id == coin_id
            )
        )
        coin = result.scalar_one_or_none()
        if not coin:
            await message.answer(f"❌ {coin_info['symbol'].upper()} is not in your watchlist.")
            return
        await session.delete(coin)
        await session.commit()
        await message.answer(f"🗑️ Removed {coin_info['name']} ({coin_info['symbol'].upper()}) from your watchlist.")

@dp.message(Command("list"))
async def list_coins(message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MonitoredCoin).where(MonitoredCoin.user_id == user.id)
        )
        coins = result.scalars().all()
        if not coins:
            await message.answer("📭 Your watchlist is empty. Use /add to add coins.")
            return
        lines = ["📋 Your Watchlist:\n"]
        for c in coins:
            price_str = f"${c.last_price:,.2f}" if c.last_price else "N/A"
            updated = c.last_updated.strftime("%Y-%m-%d %H:%M") if c.last_updated else "Never"
            lines.append(f"• {c.symbol.upper()} - {price_str} (updated: {updated} UTC)")
        await message.answer("\n".join(lines))

@dp.message(Command("price"))
async def price_command(message: Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Please provide a coin symbol or name. Example: /price BTC")
        return

    async with PriceService() as price_svc:
        coin_info = await price_svc.search_coin(query)
    if not coin_info:
        await message.answer(f"Coin '{query}' not found.")
        return
    coin_id = coin_info["id"]
    symbol = coin_info["symbol"].upper()

    async with PriceService() as price_svc:
        prices = await price_svc.get_prices([coin_id])
    if coin_id not in prices:
        await message.answer(f"Could not fetch price for {symbol}.")
        return

    price = prices[coin_id]
    await message.answer(
        f"💰 {coin_info['name']} ({symbol})\n"
        f"Current price: ${price:,.2f} USD\n"
        f"Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )

@dp.message(Command("threshold"))
async def threshold_command(message: Message, command: CommandObject):
    args = command.args
    if not args:
        await message.answer("Please provide a percentage value. Example: /threshold 5")
        return
    try:
        value = float(args)
        if value <= 0:
            await message.answer("Threshold must be a positive number.")
            return
    except ValueError:
        await message.answer("Invalid number. Please provide a number like 5.0")
        return

    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    async with AsyncSessionLocal() as session:
        user = await session.merge(user)
        user.threshold = value
        await session.commit()
    await message.answer(f"✅ Alert threshold set to {value:.2f}%.")

@dp.message(Command("notifications"))
async def notifications_command(message: Message, command: CommandObject):
    args = command.args
    if not args or args.lower() not in ("on", "off"):
        await message.answer("Usage: /notifications on  or  /notifications off")
        return

    enable = args.lower() == "on"
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    async with AsyncSessionLocal() as session:
        user = await session.merge(user)
        user.notifications_enabled = enable
        await session.commit()
    status = "enabled" if enable else "disabled"
    await message.answer(f"🔔 Notifications {status}.")

# ✅ CORRECT ERROR HANDLER
@dp.error()
async def error_handler(update: Update, exception: Exception):
    """Global error handler for the bot."""
    logger.error(f"Update {update} caused error {exception}", exc_info=True)
    
    # Try to notify the user
    if update.message:
        try:
            await update.message.answer("⚠️ An error occurred. Please try again later.")
        except Exception:
            pass
    elif update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.answer("⚠️ An error occurred. Please try again later.")
        except Exception:
            pass
    return True
EOF
