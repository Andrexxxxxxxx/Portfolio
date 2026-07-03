# bot.py
# Универсальный Telegram-бот-визитка для бизнеса
# Использует библиотеку pyTelegramBotAPI (telebot)
# Установка: pip install pyTelegramBotAPI

import telebot
from telebot import types

# ------------------- НАСТРОЙКИ (меняйте здесь) -------------------
# Вставьте сюда токен вашего бота, полученный от @BotFather
TOKEN = 'ВАШ_ТОКЕН_СЮДА'

# Все текстовые сообщения бота собраны в одном месте – легко править
TEXTS = {
    'start': (
        "🏢 Добро пожаловать в нашу компанию!\n\n"
        "Мы рады предложить вам качественные услуги. "
        "Выберите интересующий раздел с помощью кнопок ниже."
    ),
    'about': (
        "📌 О нас:\n"
        "Мы — команда профессионалов с многолетним опытом. "
        "Наша цель — предоставить лучший сервис для вашего бизнеса."
    ),
    'services': (
        "💰 Услуги и цены:\n"
        "• Консультация – 0 ₽\n"
        "• Разработка сайта – от 50 000 ₽\n"
        "• SEO-продвижение – от 30 000 ₽/мес.\n"
        "• Поддержка – от 15 000 ₽/мес.\n\n"
        "Подробный прайс вышлем по запросу."
    ),
    'contact': (
        "📞 Связаться с менеджером:\n"
        "Телефон: +7 (999) 123-45-67\n"
        "Email: info@company.ru\n"
        "Telegram: @manager_username\n\n"
        "Напишите нам – ответим в течение 15 минут!"
    ),
    'help': (
        "🤖 Доступные команды:\n"
        "/start – показать главное меню\n"
        "/help – эта справка\n\n"
        "Используйте кнопки внизу для навигации."
    ),
    'unknown': "Используйте, пожалуйста, кнопки ниже.",
}

# ------------------- КЛАВИАТУРА -------------------
def get_main_keyboard():
    """Создаёт и возвращает основную клавиатуру с тремя кнопками."""
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,   # автоматически подгоняет размер
        one_time_keyboard=False # клавиатура остаётся открытой
    )
    btn_about = types.KeyboardButton("О нас")
    btn_services = types.KeyboardButton("Услуги и Цены")
    btn_contact = types.KeyboardButton("Связаться с менеджером")
    # Добавляем кнопки (можно расположить в ряд или столбик)
    keyboard.add(btn_about, btn_services, btn_contact)
    return keyboard

# ------------------- ОБРАБОТЧИКИ КОМАНД -------------------
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветствие и показ главного меню."""
    bot.send_message(
        message.chat.id,
        TEXTS['start'],
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    """Показывает справку."""
    bot.send_message(
        message.chat.id,
        TEXTS['help'],
        reply_markup=get_main_keyboard()
    )

# ------------------- ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ (КНОПОК) -------------------
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Обрабатывает нажатия на reply-кнопки."""
    text = message.text
    if text == "О нас":
        bot.send_message(message.chat.id, TEXTS['about'])
    elif text == "Услуги и Цены":
        bot.send_message(message.chat.id, TEXTS['services'])
    elif text == "Связаться с менеджером":
        bot.send_message(message.chat.id, TEXTS['contact'])
    else:
        # Если пользователь написал что-то другое – напоминаем про кнопки
        bot.send_message(
            message.chat.id,
            TEXTS['unknown'],
            reply_markup=get_main_keyboard()
        )

# ------------------- ЗАПУСК БОТА -------------------
if __name__ == '__main__':
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    bot.infinity_polling()