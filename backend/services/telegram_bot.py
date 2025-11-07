import os
import logging
import asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.admin_id = os.environ.get('ADMIN_TELEGRAM_ID')
        self.webapp_url = os.environ.get('WEBAPP_URL', 'https://tyres.vpnsuba.ru')
        self.application = None
        
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set")
            self.bot = None
        else:
            try:
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram bot initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self.bot = None
    
    async def start_bot_polling(self):
        """Запустить бота в режиме polling для обработки команд"""
        if not self.bot_token:
            logger.warning("Cannot start bot polling: token not set")
            return
        
        try:
            # Создаём приложение для обработки команд
            self.application = Application.builder().token(self.bot_token).build()
            
            # Регистрируем обработчики команд
            self.application.add_handler(CommandHandler("start", self._handle_start))
            self.application.add_handler(CommandHandler("help", self._handle_help))
            
            # Запускаем polling в фоне
            logger.info("Starting Telegram bot polling...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            logger.info("Telegram bot polling started successfully!")
        except Exception as e:
            logger.error(f"Failed to start bot polling: {e}")
    
    async def stop_bot_polling(self):
        """Остановить polling бота"""
        if self.application:
            try:
                logger.info("Stopping Telegram bot polling...")
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Telegram bot polling stopped")
            except Exception as e:
                logger.error(f"Error stopping bot polling: {e}")
    
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Отправляем приветственное сообщение
        welcome_text = (
            f"🎉 Добро пожаловать, {user.first_name}!\n\n"
            f"🚗 <b>Интернет-магазин шин и дисков</b>\n\n"
            f"У нас вы найдёте:\n"
            f"✅ Самые выгодные цены на шины и диски\n"
            f"✅ Огромный выбор брендов и моделей\n"
            f"✅ Подбор по автомобилю\n"
            f"✅ Доставка в ваш город\n\n"
            f"Нажмите кнопку <b>\"Магазин\"</b> внизу слева и подберите шины для вашего автомобиля!\n\n"
            f"💰 Наценка минимальная, качество — максимальное!"
        )
        
        await update.message.reply_text(welcome_text, parse_mode='HTML')
        logger.info(f"User {user.id} (@{user.username}) started the bot")
        
        # Уведомляем админа о новом пользователе (если это не сам админ)
        if self.admin_id and str(user.id) != self.admin_id:
            await self.notify_admin_new_visitor(
                telegram_id=str(user.id),
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
    
    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "🤖 <b>Команды бота:</b>\n\n"
            "/start - Открыть магазин\n"
            "/help - Показать эту справку\n\n"
            "Используйте кнопку \"🛒 Открыть магазин\" для доступа к каталогу товаров."
        )
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def send_message(self, chat_id: str, text: str) -> bool:
        """Отправить сообщение пользователю"""
        if not self.bot:
            logger.warning("Bot not initialized, skipping message")
            return False
        
        try:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
            logger.info(f"Message sent to {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False
    
    async def notify_admin_new_order(
        self, 
        order_id: str, 
        user_name: str, 
        total_amount: float,
        items_count: int
    ) -> bool:
        """Уведомить админа о новом заказе"""
        message = (
            f"🔔 <b>Новый заказ!</b>\n\n"
            f"📦 Заказ: <b>#{order_id}</b>\n"
            f"👤 Клиент: {user_name}\n"
            f"📊 Товаров: {items_count} шт.\n"
            f"💰 Сумма: <b>{total_amount:,.2f} ₽</b>\n\n"
            f"⚡️ Требуется подтверждение в админ-панели"
        )
        return await self.send_message(self.admin_id, message)
    
    async def notify_user_order_confirmed(
        self,
        user_telegram_id: str,
        order_id: str,
        admin_comment: Optional[str] = None
    ) -> bool:
        """Уведомить клиента о подтверждении заказа"""
        message = (
            f"✅ <b>Заказ подтвержден!</b>\n\n"
            f"📦 Заказ: <b>#{order_id}</b>\n"
            f"🚀 Ваш заказ отправлен поставщику\n\n"
        )
        if admin_comment:
            message += f"💬 Комментарий: {admin_comment}\n\n"
        message += "Мы сообщим вам о дальнейших изменениях статуса."
        
        return await self.send_message(user_telegram_id, message)
    
    async def notify_user_order_rejected(
        self,
        user_telegram_id: str,
        order_id: str,
        reason: str
    ) -> bool:
        """Уведомить клиента об отклонении заказа"""
        message = (
            f"❌ <b>Заказ отклонен</b>\n\n"
            f"📦 Заказ: <b>#{order_id}</b>\n"
            f"📝 Причина: {reason}\n\n"
            f"Свяжитесь с нами для уточнения деталей."
        )
        return await self.send_message(user_telegram_id, message)
    
    async def notify_user_order_sent_to_supplier(
        self,
        user_telegram_id: str,
        order_id: str,
        supplier_order_number: str
    ) -> bool:
        """Уведомить клиента об отправке заказа поставщику"""
        message = (
            f"📦 <b>Заказ в обработке</b>\n\n"
            f"📦 Ваш заказ: <b>#{order_id}</b>\n"
            f"🏭 Номер у поставщика: <b>{supplier_order_number}</b>\n\n"
            f"Ожидайте дальнейших обновлений."
        )
        return await self.send_message(user_telegram_id, message)
    
    async def notify_user_order_completed(
        self,
        user_telegram_id: str,
        order_id: str
    ) -> bool:
        """Уведомить клиента о выполнении заказа"""
        message = (
            f"🎉 <b>Заказ выполнен!</b>\n\n"
            f"📦 Заказ: <b>#{order_id}</b>\n\n"
            f"Благодарим за покупку! 🙏"
        )
        return await self.send_message(user_telegram_id, message)
    
    async def notify_admin_new_visitor(
        self,
        telegram_id: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> bool:
        """Уведомить админа о новом посетителе магазина"""
        # Формируем имя пользователя
        user_display = ""
        if first_name or last_name:
            name_parts = []
            if first_name:
                name_parts.append(first_name)
            if last_name:
                name_parts.append(last_name)
            user_display = " ".join(name_parts)
        
        message = (
            f"👋 <b>Новый посетитель в магазине!</b>\n\n"
            f"🆔 ID: <code>{telegram_id}</code>\n"
        )
        
        if username:
            message += f"👤 Username: @{username}\n"
        
        if user_display:
            message += f"📝 Имя: {user_display}\n"
        
        return await self.send_message(self.admin_id, message)

# Singleton instance
telegram_notifier = None

def get_telegram_notifier() -> TelegramNotifier:
    global telegram_notifier
    if telegram_notifier is None:
        telegram_notifier = TelegramNotifier()
    return telegram_notifier
