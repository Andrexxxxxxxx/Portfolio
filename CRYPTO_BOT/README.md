# Crypto Price Alert Telegram Bot

A production-ready Telegram bot that monitors cryptocurrency prices and sends alerts on significant changes.

## Features

- Monitor any coin available on CoinGecko.
- Set custom alert thresholds (default 5%).
- Toggle notifications on/off.
- View current prices and watchlist.
- Fully async, uses SQLite with SQLAlchemy.
- Periodic price checks every hour (configurable).

## Installation

### Prerequisites

- Python 3.12+
- Telegram Bot Token (from @BotFather)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crypto-bot.git
   cd crypto-bot
