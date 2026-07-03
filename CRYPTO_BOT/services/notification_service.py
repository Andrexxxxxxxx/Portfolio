import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import format_price, format_percent

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_alert(self, user_telegram_id: int, coin_name: str, symbol: str,
                         old_price: float, new_price: float, change_percent: float):
        """
        Send price alert message.
        """
        direction = "Increased" if change_percent > 0 else "Decreased"
        emoji = "📈" if change_percent > 0 else "📉"

        message = (
            f"{emoji} <b>Price Alert</b>\n\n"
            f"Coin: {coin_name} ({symbol})\n"
            f"Direction: {direction}\n"
            f"Previous price: ${format_price(old_price)}\n"
            f"Current price: ${format_price(new_price)}\n"
            f"Change: {format_percent(change_percent)}\n"
            f"Time: {self._current_utc()}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="View price", callback_data=f"price_{symbol}")]
        ])

        try:
            await self.bot.send_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=keyboard
            )
            logger.info(f"Alert sent to user {user_telegram_id} for {symbol}")
        except Exception as e:
            logger.error(f"Failed to send alert to {user_telegram_id}: {e}")

    def _current_utc(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
