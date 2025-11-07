#!/usr/bin/env python3
"""
Telegram бот для магазина шин и дисков
Обрабатывает команду /start и отправляет приветствие
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://tyres.vpnsuba.ru')
ADMIN_TELEGRAM_ID = os.environ.get('ADMIN_TELEGRAM_ID')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Отправляем приветственное сообщение
    welcome_text = (
        f"🎉 Добро пожаловать, {user.first_name}!\n\n"
        f"🚗 <b>Интернет-магазин шин и дисков 4tochki</b>\n\n"
        f"У нас вы найдёте:\n"
        f"✅ Самые выгодные цены на шины и диски\n"
        f"✅ Огромный выбор брендов и моделей\n"
        f"✅ Подбор по автомобилю\n"
        f"✅ Доставка в ваш город\n\n"
        f"Нажмите кнопку <b>\"🛒 Открыть магазин\"</b> ниже и подберите шины для вашего автомобиля!\n\n"
        f"💰 Наценка минимальная, качество — максимальное!"
    )
    
    # Создаём кнопку для открытия Mini App
    keyboard = [
        [InlineKeyboardButton("🛒 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    # Логируем событие
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
    # Уведомляем админа о новом пользователе (если это не сам админ)
    if ADMIN_TELEGRAM_ID and str(user.id) != ADMIN_TELEGRAM_ID:
        admin_notification = (
            f"👋 <b>Новый посетитель!</b>\n\n"
            f"🆔 ID: <code>{user.id}</code>\n"
        )
        if user.username:
            admin_notification += f"👤 Username: @{user.username}\n"
        if user.first_name or user.last_name:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            admin_notification += f"📝 Имя: {name}\n"
        
        try:
            await context.bot.send_message(
                chat_id=int(ADMIN_TELEGRAM_ID),
                text=admin_notification,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = (
        "🤖 <b>Команды бота:</b>\n\n"
        "/start - Открыть магазин\n"
        "/help - Показать эту справку\n\n"
        "Используйте кнопку \"🛒 Открыть магазин\" для доступа к каталогу товаров."
    )
    await update.message.reply_text(help_text, parse_mode='HTML')


def main() -> None:
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Запускаем бота
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
